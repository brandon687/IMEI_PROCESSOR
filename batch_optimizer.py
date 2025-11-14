"""
Optimized Batch IMEI Processing for High-Volume Submissions
Handles 20,000+ devices efficiently with progress tracking
"""

import time
import logging
from typing import List, Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from gsm_fusion_client import GSMFusionClient, GSMFusionAPIError

logger = logging.getLogger(__name__)


class BatchIMEIProcessor:
    """
    High-performance batch IMEI processor

    Features:
    - Chunked processing (avoid overwhelming API)
    - Configurable concurrency (10-50 workers)
    - Progress callbacks for UI updates
    - Automatic retry on failures
    - Rate limiting protection
    """

    def __init__(
        self,
        max_workers: int = 20,
        chunk_size: int = 100,
        rate_limit_delay: float = 0.1
    ):
        """
        Initialize batch processor

        Args:
            max_workers: Number of concurrent threads (default 20)
            chunk_size: IMEIs per API call (default 100, adjust based on API limits)
            rate_limit_delay: Delay between chunks to avoid rate limits (seconds)
        """
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.rate_limit_delay = rate_limit_delay

    def _chunk_list(self, items: List[str], chunk_size: int) -> List[List[str]]:
        """Split list into chunks"""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    def _submit_chunk(
        self,
        imeis: List[str],
        service_id: str,
        chunk_num: int,
        total_chunks: int
    ) -> Dict:
        """
        Submit a chunk of IMEIs

        Returns:
            Dict with 'successful', 'duplicates', 'errors', 'orders'
        """
        result = {
            'successful': [],
            'duplicates': [],
            'errors': [],
            'orders': []
        }

        try:
            client = GSMFusionClient()

            # Try batch submission first (if API supports it)
            if self.chunk_size > 1:
                try:
                    api_result = client.place_imei_order(imei=imeis, network_id=service_id)

                    # Process successful orders
                    if api_result.get('orders'):
                        for order in api_result['orders']:
                            result['successful'].append({
                                'imei': order.get('imei'),
                                'order_id': order.get('id'),
                                'status': order.get('status')
                            })
                            result['orders'].append(order)

                    # Process duplicates
                    if api_result.get('duplicates'):
                        result['duplicates'].extend(api_result['duplicates'])

                    # Process errors
                    if api_result.get('errors'):
                        for error in api_result['errors']:
                            result['errors'].append({
                                'imei': 'batch',
                                'message': error
                            })

                    client.close()
                    logger.info(f"Chunk {chunk_num}/{total_chunks}: {len(result['successful'])} successful")
                    return result

                except Exception as e:
                    logger.warning(f"Batch submission failed for chunk {chunk_num}, falling back to individual: {e}")
                    client.close()

            # Fallback: Submit individually (if batch fails or chunk_size=1)
            for imei in imeis:
                try:
                    temp_client = GSMFusionClient()
                    api_result = temp_client.place_imei_order(imei=imei, network_id=service_id)
                    temp_client.close()

                    if api_result.get('orders'):
                        order = api_result['orders'][0]
                        result['successful'].append({
                            'imei': imei,
                            'order_id': order.get('id'),
                            'status': order.get('status')
                        })
                        result['orders'].append(order)
                    elif api_result.get('duplicates'):
                        result['duplicates'].append(imei)
                    elif api_result.get('errors'):
                        result['errors'].append({
                            'imei': imei,
                            'message': api_result['errors'][0]
                        })
                except Exception as e:
                    result['errors'].append({
                        'imei': imei,
                        'message': str(e)
                    })

            logger.info(f"Chunk {chunk_num}/{total_chunks}: {len(result['successful'])} successful (individual mode)")
            return result

        except Exception as e:
            logger.error(f"Chunk {chunk_num} failed completely: {e}")
            for imei in imeis:
                result['errors'].append({
                    'imei': imei,
                    'message': f"Chunk processing error: {str(e)}"
                })
            return result

    def process_batch(
        self,
        imeis: List[str],
        service_id: str,
        progress_callback: Optional[Callable[[int, int, Dict], None]] = None
    ) -> Dict:
        """
        Process large batch of IMEIs with progress tracking

        Args:
            imeis: List of IMEI numbers
            service_id: Service ID to use
            progress_callback: Function(processed, total, result) called after each chunk

        Returns:
            Dict with aggregated results: {
                'total': int,
                'successful': int,
                'duplicates': int,
                'errors': int,
                'orders': List[Dict],
                'error_details': List[Dict],
                'processing_time': float
            }
        """
        start_time = time.time()

        # Split into chunks
        chunks = self._chunk_list(imeis, self.chunk_size)
        total_chunks = len(chunks)

        logger.info(f"Processing {len(imeis)} IMEIs in {total_chunks} chunks with {self.max_workers} workers")

        # Aggregate results
        aggregate = {
            'total': len(imeis),
            'successful': 0,
            'duplicates': 0,
            'errors': 0,
            'orders': [],
            'error_details': [],
            'processing_time': 0
        }

        processed_chunks = 0

        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(
                    self._submit_chunk,
                    chunk,
                    service_id,
                    i + 1,
                    total_chunks
                ): (i, chunk)
                for i, chunk in enumerate(chunks)
            }

            # Process results as they complete
            for future in as_completed(future_to_chunk):
                chunk_num, chunk_imeis = future_to_chunk[future]

                try:
                    result = future.result()

                    # Aggregate results
                    aggregate['successful'] += len(result['successful'])
                    aggregate['duplicates'] += len(result['duplicates'])
                    aggregate['errors'] += len(result['errors'])
                    aggregate['orders'].extend(result['orders'])
                    aggregate['error_details'].extend(result['errors'])

                    processed_chunks += 1

                    # Call progress callback
                    if progress_callback:
                        progress_callback(
                            processed_chunks * self.chunk_size,
                            len(imeis),
                            aggregate
                        )

                    # Rate limiting delay
                    if self.rate_limit_delay > 0:
                        time.sleep(self.rate_limit_delay)

                except Exception as e:
                    logger.error(f"Failed to process chunk {chunk_num + 1}: {e}")
                    aggregate['errors'] += len(chunk_imeis)
                    for imei in chunk_imeis:
                        aggregate['error_details'].append({
                            'imei': imei,
                            'message': f"Chunk execution error: {str(e)}"
                        })

        aggregate['processing_time'] = time.time() - start_time

        logger.info(
            f"Batch complete: {aggregate['successful']} successful, "
            f"{aggregate['duplicates']} duplicates, {aggregate['errors']} errors "
            f"in {aggregate['processing_time']:.2f} seconds"
        )

        return aggregate


def estimate_processing_time(num_imeis: int, workers: int = 20, chunk_size: int = 100) -> float:
    """
    Estimate processing time for batch submission

    Args:
        num_imeis: Number of IMEIs to process
        workers: Number of concurrent workers
        chunk_size: IMEIs per chunk

    Returns:
        Estimated time in seconds
    """
    # Assumptions:
    # - Each API call takes ~2-5 seconds (average 3.5)
    # - Batch calls are same as individual (conservative estimate)

    avg_api_time = 3.5  # seconds

    if chunk_size > 1:
        # Batch mode: fewer API calls
        total_chunks = (num_imeis + chunk_size - 1) // chunk_size
    else:
        # Individual mode
        total_chunks = num_imeis

    # With parallel workers
    parallel_time = (total_chunks / workers) * avg_api_time

    return parallel_time


def get_recommended_settings(num_imeis: int) -> Dict:
    """
    Get recommended processing settings for given volume

    Args:
        num_imeis: Number of IMEIs to process

    Returns:
        Dict with recommended settings
    """
    if num_imeis < 100:
        return {
            'max_workers': 10,
            'chunk_size': 1,  # Individual submissions for small batches
            'rate_limit_delay': 0.05,
            'estimated_time': estimate_processing_time(num_imeis, 10, 1),
            'strategy': 'Individual submissions (small batch)'
        }

    elif num_imeis < 1000:
        return {
            'max_workers': 15,
            'chunk_size': 50,  # Try 50 per batch
            'rate_limit_delay': 0.1,
            'estimated_time': estimate_processing_time(num_imeis, 15, 50),
            'strategy': 'Medium batches with moderate concurrency'
        }

    elif num_imeis < 10000:
        return {
            'max_workers': 20,
            'chunk_size': 100,  # 100 per batch
            'rate_limit_delay': 0.1,
            'estimated_time': estimate_processing_time(num_imeis, 20, 100),
            'strategy': 'Large batches with high concurrency'
        }

    else:  # 10K+
        return {
            'max_workers': 30,
            'chunk_size': 100,  # Conservative chunk size
            'rate_limit_delay': 0.05,  # Minimal delay (fast mode)
            'estimated_time': estimate_processing_time(num_imeis, 30, 100),
            'strategy': 'Maximum performance (30 workers, 100 per chunk)'
        }


# Example usage
if __name__ == '__main__':
    # Test with sample data
    def progress_callback(processed, total, result):
        percent = (processed / total) * 100
        print(f"Progress: {processed}/{total} ({percent:.1f}%) - "
              f"Success: {result['successful']}, Errors: {result['errors']}")

    # Simulate 20K submission
    print("\n" + "="*80)
    print("PERFORMANCE ESTIMATES FOR YOUR 20K WEEKLY VOLUME")
    print("="*80)

    for volume in [100, 1000, 5000, 10000, 20000, 30000]:
        settings = get_recommended_settings(volume)
        print(f"\n{volume:,} devices:")
        print(f"  Workers: {settings['max_workers']}")
        print(f"  Chunk Size: {settings['chunk_size']}")
        print(f"  Strategy: {settings['strategy']}")
        print(f"  Estimated Time: {settings['estimated_time']/60:.1f} minutes")
