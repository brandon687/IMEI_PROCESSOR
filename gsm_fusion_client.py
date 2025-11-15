"""
GSM Fusion API Client - Professional Implementation
====================================================
A modern Python client for the GSM Fusion API (hammerfusion.com) that automates
IMEI data processing and GSX detail retrieval.

Author: Auto-generated
Version: 1.0.0
"""

import os
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = 1
    COMPLETED = 2
    REJECTED = 3
    IN_PROCESS = 4


@dataclass
class IMEIOrder:
    """Represents an IMEI order"""
    id: str
    imei: str
    package: str
    status: str
    code: Optional[str] = None
    requested_at: Optional[str] = None


@dataclass
class ServiceInfo:
    """Represents a service/package information"""
    package_id: str
    category: str
    title: str
    price: str
    delivery_time: str
    details: str


class GSMFusionAPIError(Exception):
    """Base exception for GSM Fusion API errors"""
    pass


class GSMFusionClient:
    """
    Professional GSM Fusion API Client

    This client provides a complete interface to the GSM Fusion API,
    handling authentication, requests, response parsing, and error handling.

    Example:
        client = GSMFusionClient(api_key="your-key", username="your-username")
        services = client.get_imei_services()
        order = client.place_imei_order(imei="123456789012345", network_id="1")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize the GSM Fusion API client

        Args:
            api_key: API key (defaults to GSM_FUSION_API_KEY env var)
            username: Username (defaults to GSM_FUSION_USERNAME env var)
            base_url: Base API URL (defaults to GSM_FUSION_BASE_URL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key or os.getenv('GSM_FUSION_API_KEY')
        self.username = username or os.getenv('GSM_FUSION_USERNAME')
        self.base_url = base_url or os.getenv(
            'GSM_FUSION_BASE_URL',
            'https://hammerfusion.com'
        )
        self.timeout = timeout

        if not self.api_key:
            raise GSMFusionAPIError(
                "API key is required. Set GSM_FUSION_API_KEY environment variable "
                "or pass api_key parameter."
            )

        if not self.username:
            raise GSMFusionAPIError(
                "Username is required. Set GSM_FUSION_USERNAME environment variable "
                "or pass username parameter."
            )

        # Setup session with retry logic
        self.session = self._create_session(max_retries)

        logger.info(f"GSM Fusion client initialized for user: {self.username}")

    def _create_session(self, max_retries: int) -> requests.Session:
        """Create a requests session with retry configuration"""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        action: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Make an API request

        Args:
            action: API action to perform
            parameters: Additional parameters for the request

        Returns:
            XML response as string

        Raises:
            GSMFusionAPIError: If the request fails
        """
        if parameters is None:
            parameters = {}

        # Add authentication parameters
        parameters['apiKey'] = self.api_key
        parameters['userId'] = self.username
        parameters['action'] = action

        url = f"{self.base_url}/gsmfusion_api/index.php"

        try:
            logger.debug(f"Making request to {url} with action: {action}")
            logger.debug(f"Request parameters: {parameters}")

            import time
            http_start = time.time()
            response = self.session.post(
                url,
                data=parameters,
                timeout=self.timeout
            )
            http_duration = time.time() - http_start

            response.raise_for_status()

            # CRITICAL DEBUG: Log response details
            logger.info(f"HTTP request for {action} completed in {http_duration:.2f}s")
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response length: {len(response.text)} bytes")
            logger.info(f"Response content (first 1000 chars): {response.text[:1000]}")

            if len(response.text) > 1000:
                logger.info(f"Response content (last 500 chars): ...{response.text[-500:]}")

            return response.text

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for action: {action}")
            raise GSMFusionAPIError(f"Request timed out after {self.timeout} seconds")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for action {action}: {str(e)}")
            raise GSMFusionAPIError(f"API request failed: {str(e)}")

    def _parse_xml_response(self, xml_string: str) -> Dict[str, Any]:
        """
        Parse XML response into a dictionary

        Args:
            xml_string: XML response string

        Returns:
            Parsed response as dictionary (ALWAYS returns dict, never string)

        Raises:
            GSMFusionAPIError: If XML parsing fails or contains errors
        """
        try:
            # FIX: API sometimes returns malformed XML with <?phpxml instead of <?xml
            # This is a critical bug fix for the 0 services issue
            if xml_string.startswith('<?phpxml'):
                logger.warning("Detected malformed XML with '<?phpxml' declaration - fixing automatically")
                xml_string = xml_string.replace('<?phpxml', '<?xml', 1)

            root = ET.fromstring(xml_string)

            # Check for errors in response
            error_elem = root.find('.//error')
            if error_elem is not None and error_elem.text:
                logger.error(f"API returned error: {error_elem.text}")
                raise GSMFusionAPIError(f"API Error: {error_elem.text}")

            # Convert XML to dict
            result = self._xml_to_dict(root)

            # CRITICAL: _xml_to_dict might return a string for leaf nodes
            # We MUST always return a dict from this method
            if isinstance(result, str):
                # Wrap string result in dict with root element name
                return {root.tag: result}
            elif not isinstance(result, dict):
                # Safety: any other non-dict type, wrap it
                return {root.tag: result}

            return result

        except ET.ParseError as e:
            logger.error(f"XML parsing failed: {str(e)}")
            raise GSMFusionAPIError(f"Failed to parse API response: {str(e)}")

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Recursively convert XML element to dictionary"""
        result: Dict[str, Any] = {}

        # Add element attributes if present
        if element.attrib:
            result.update(element.attrib)

        # Check if element has children
        has_children = len(element) > 0

        # If element has text but no children, store text in the result dict
        if element.text and element.text.strip() and not has_children:
            # If we already have attributes, add text as 'text' key
            if result:
                result['text'] = element.text.strip()
            else:
                # No attributes and no children, just return the text
                return element.text.strip()

        # Process child elements
        for child in element:
            child_data = self._xml_to_dict(child)

            if child.tag in result:
                # Convert to list if multiple elements with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result if result else (element.text.strip() if element.text else {})

    # API Methods

    def get_imei_services(self) -> List[ServiceInfo]:
        """
        Get list of all available IMEI services

        Returns:
            List of ServiceInfo objects

        Example:
            services = client.get_imei_services()
            for service in services:
                print(f"{service.title}: ${service.price}")
        """
        logger.info("Fetching IMEI services list")

        xml_response = self._make_request('imeiservices')

        # DEBUG: Log first 500 chars of XML response
        logger.debug(f"Raw XML response (first 500 chars): {xml_response[:500]}")

        data = self._parse_xml_response(xml_response)

        # DEBUG: Log the parsed data structure
        logger.debug(f"Parsed data keys: {data.keys() if isinstance(data, dict) else 'NOT A DICT'}")
        logger.debug(f"Parsed data type: {type(data)}")
        if isinstance(data, dict) and len(data) < 5:
            logger.debug(f"Full parsed data: {data}")

        services = []
        # Packages are directly under root, not nested
        packages = data.get('Package', [])

        logger.info(f"Initial packages extraction: found {len(packages) if isinstance(packages, list) else 1 if packages else 0} items")

        # Try alternative keys if Package is empty
        if not packages:
            logger.warning("No 'Package' key found in response, trying alternative keys...")
            logger.info(f"Available keys in response: {list(data.keys())}")

            # Check if data has nested structure
            for key in ['services', 'Services', 'service', 'Service', 'PACKAGE', 'package']:
                if key in data:
                    packages = data[key]
                    logger.info(f"✓ Found packages under key '{key}': {len(packages) if isinstance(packages, list) else 1 if packages else 0} items")
                    break
            else:
                logger.error(f"❌ NO SERVICES FOUND! Checked all keys. Response structure: {data}")

        # Ensure packages is a list
        if not isinstance(packages, list):
            packages = [packages] if packages else []
            logger.debug(f"Converted single package to list: {len(packages)} items")

        for pkg in packages:
            # Skip non-dictionary packages (malformed data)
            if not isinstance(pkg, dict):
                logger.warning(f"Skipping non-dict package: {type(pkg)}")
                continue

            service = ServiceInfo(
                package_id=pkg.get('PackageId', ''),
                category=pkg.get('Category', ''),
                title=pkg.get('PackageTitle', ''),
                price=pkg.get('PackagePrice', ''),
                delivery_time=pkg.get('TimeTaken', ''),
                details=pkg.get('MustRead', '')
            )
            services.append(service)

        logger.info(f"Retrieved {len(services)} IMEI services")
        return services

    def get_file_services(self) -> List[ServiceInfo]:
        """
        Get list of all available file services

        Returns:
            List of ServiceInfo objects
        """
        logger.info("Fetching file services list")

        xml_response = self._make_request('fileservices')
        data = self._parse_xml_response(xml_response)

        services = []
        # Packages are directly under root, not nested
        packages = data.get('Package', [])

        if not isinstance(packages, list):
            packages = [packages]

        for pkg in packages:
            # Skip non-dictionary packages (malformed data)
            if not isinstance(pkg, dict):
                logger.warning(f"Skipping non-dict package: {type(pkg)}")
                continue

            service = ServiceInfo(
                package_id=pkg.get('PackageId', ''),
                category=pkg.get('Category', ''),
                title=pkg.get('PackageTitle', ''),
                price=pkg.get('PackagePrice', ''),
                delivery_time=pkg.get('TimeTaken', ''),
                details=pkg.get('MustRead', '')
            )
            services.append(service)

        logger.info(f"Retrieved {len(services)} file services")
        return services

    def place_imei_order(
        self,
        imei: Union[str, List[str]],
        network_id: str,
        force_recheck: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Place an IMEI order

        Args:
            imei: Single IMEI or list of IMEIs
            network_id: Network/Service ID
            force_recheck: If True, treats "already exists" errors as errors (not duplicates) for visibility
            **kwargs: Optional parameters (modelNo, operatorId, serviceId,
                     providerId, modelId, mobileId, mep, serialNo, prd,
                     pin, kbh, zte, otherId, other)

        Returns:
            Dictionary containing order results with 'orders', 'duplicates',
            and 'errors' keys

        Example:
            result = client.place_imei_order(
                imei="123456789012345",
                network_id="1"
            )

            # Multiple IMEIs
            result = client.place_imei_order(
                imei=["123456789012345", "123456789012346"],
                network_id="1"
            )
        """
        # Format IMEI parameter
        if isinstance(imei, list):
            imei_str = ','.join(imei)
            logger.info(f"Placing order for {len(imei)} IMEIs")
        else:
            imei_str = imei
            logger.info(f"Placing order for IMEI: {imei}")

        parameters = {
            'imei': imei_str,
            'networkId': network_id,
            **kwargs
        }

        xml_response = self._make_request('placeorder', parameters)
        data = self._parse_xml_response(xml_response)

        result = {
            'orders': [],
            'duplicates': [],
            'errors': []
        }

        # Handle if data is a string (error message)
        if isinstance(data, str):
            # Check if it's a duplicate error
            if 'already exists' in data.lower():
                # If force_recheck is enabled, treat as error to show in UI
                if force_recheck:
                    result['errors'].append(f"FORCE RECHECK FAILED: {data} (GSM Fusion API rejected re-submission)")
                    logger.error(f"Force recheck failed - API still rejects: {data}")
                else:
                    # Normal behavior: mark as duplicate
                    if isinstance(imei, list):
                        result['duplicates'].extend(imei)
                    else:
                        result['duplicates'].append(imei)
                    logger.warning(f"Duplicate IMEI(s): {data}")
            else:
                result['errors'].append(data)
                logger.error(f"Order placement failed: {data}")
            return result

        # Parse successful orders
        # Try both structures: with and without 'result' wrapper
        imeis_data = data.get('imeis', {}) or data.get('result', {}).get('imeis', {}) if isinstance(data, dict) else {}
        if imeis_data:
            imei_list = imeis_data if isinstance(imeis_data, list) else [imeis_data]
            for imei_data in imei_list:
                result['orders'].append({
                    'id': imei_data.get('id'),
                    'imei': imei_data.get('imei'),
                    'status': imei_data.get('status')
                })

        # Parse duplicates
        duplicates_data = data.get('imeiduplicates', {}) or data.get('result', {}).get('imeiduplicates', {})
        if duplicates_data:
            dup_list = duplicates_data if isinstance(duplicates_data, list) else [duplicates_data]
            for dup in dup_list:
                if 'imei' in dup:
                    result['duplicates'].extend(dup['imei'].split(','))

        logger.info(
            f"Order placed: {len(result['orders'])} successful, "
            f"{len(result['duplicates'])} duplicates"
        )

        return result

    def get_imei_orders(
        self,
        order_ids: Union[str, List[str]]
    ) -> List[IMEIOrder]:
        """
        Get status of IMEI orders

        Args:
            order_ids: Single order ID or list of order IDs

        Returns:
            List of IMEIOrder objects

        Example:
            orders = client.get_imei_orders("12345")
            for order in orders:
                print(f"{order.imei}: {order.status} - {order.code}")
        """
        # Format order IDs parameter
        if isinstance(order_ids, list):
            order_ids_str = ','.join(str(id) for id in order_ids)
            logger.info(f"Fetching status for {len(order_ids)} orders")
        else:
            order_ids_str = str(order_ids)
            logger.info(f"Fetching status for order: {order_ids}")

        xml_response = self._make_request('getimeis', {'orderIds': order_ids_str})

        # Log raw XML for debugging
        logger.info(f"Raw XML response (first 1000 chars): {xml_response[:1000]}")

        data = self._parse_xml_response(xml_response)

        logger.info(f"get_imei_orders API response data structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        if isinstance(data, dict) and 'result' in data:
            logger.info(f"  result keys: {list(data['result'].keys()) if isinstance(data['result'], dict) else type(data['result'])}")

        # Log full parsed data for debugging
        logger.info(f"Full parsed data: {data}")

        orders = []
        # Try both response structures: direct 'imeis' or nested in 'result'
        imeis_data = data.get('imeis', []) or data.get('result', {}).get('imeis', [])

        if not isinstance(imeis_data, list):
            imeis_data = [imeis_data]

        logger.info(f"Parsed {len(imeis_data)} order(s) from API response")

        for imei_data in imeis_data:
            order = IMEIOrder(
                id=imei_data.get('id', ''),
                imei=imei_data.get('imei', ''),
                package=imei_data.get('package', ''),
                status=imei_data.get('status', ''),
                code=imei_data.get('code'),
                requested_at=imei_data.get('requestedat')
            )
            orders.append(order)

        logger.info(f"Retrieved {len(orders)} order(s)")
        return orders

    def place_file_order(
        self,
        network_id: str,
        file_name: str,
        file_data: bytes
    ) -> Dict[str, Any]:
        """
        Place a file order

        Args:
            network_id: Network/Service ID
            file_name: Name of the file
            file_data: File content as bytes

        Returns:
            Dictionary containing order information

        Example:
            with open('device.bcl', 'rb') as f:
                result = client.place_file_order(
                    network_id="1",
                    file_name="device.bcl",
                    file_data=f.read()
                )
        """
        logger.info(f"Placing file order: {file_name}")

        parameters = {
            'networkId': network_id,
            'fileName': file_name,
            'fileData': file_data
        }

        xml_response = self._make_request('placefileorder', parameters)
        data = self._parse_xml_response(xml_response)

        result = data.get('result', {})
        logger.info(f"File order placed with ID: {result.get('orderId')}")

        return result

    def get_file_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get status of a file order

        Args:
            order_id: Order ID

        Returns:
            Dictionary containing order status and details
        """
        logger.info(f"Fetching file order: {order_id}")

        xml_response = self._make_request('getfileorder', {'orderId': order_id})
        data = self._parse_xml_response(xml_response)

        return data.get('result', {})

    def get_meps_list(self) -> List[Dict[str, str]]:
        """Get list of MEPs (for BlackBerry services)"""
        logger.info("Fetching MEPs list")

        xml_response = self._make_request('mepslist')
        data = self._parse_xml_response(xml_response)

        meps = data.get('MEPs', {}).get('MEP', [])
        if not isinstance(meps, list):
            meps = [meps]

        return meps

    def get_prds_list(self) -> List[Dict[str, str]]:
        """Get list of PRDs"""
        logger.info("Fetching PRDs list")

        xml_response = self._make_request('prdslist')
        data = self._parse_xml_response(xml_response)

        prds = data.get('PRDs', {}).get('PRD', [])
        if not isinstance(prds, list):
            prds = [prds]

        return prds

    def wait_for_order_completion(
        self,
        order_id: str,
        check_interval: int = 60,
        max_wait_time: int = 3600
    ) -> IMEIOrder:
        """
        Wait for an order to complete (polling)

        Args:
            order_id: Order ID to monitor
            check_interval: Seconds between status checks (default: 60)
            max_wait_time: Maximum time to wait in seconds (default: 3600)

        Returns:
            Completed IMEIOrder object

        Raises:
            GSMFusionAPIError: If order is rejected or timeout occurs
        """
        logger.info(f"Waiting for order {order_id} to complete...")

        start_time = time.time()

        while True:
            # Check if max wait time exceeded
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                raise GSMFusionAPIError(
                    f"Order {order_id} did not complete within {max_wait_time} seconds"
                )

            # Get order status
            orders = self.get_imei_orders(order_id)
            if not orders:
                raise GSMFusionAPIError(f"Order {order_id} not found")

            order = orders[0]

            # Check status
            if order.status.lower() == 'completed':
                logger.info(f"Order {order_id} completed successfully")
                return order

            elif order.status.lower() == 'rejected':
                logger.error(f"Order {order_id} was rejected")
                raise GSMFusionAPIError(f"Order {order_id} was rejected")

            # Wait before next check
            logger.debug(
                f"Order {order_id} status: {order.status}. "
                f"Checking again in {check_interval} seconds..."
            )
            time.sleep(check_interval)

    def close(self):
        """Close the session"""
        self.session.close()
        logger.info("GSM Fusion client session closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Example usage
    print("GSM Fusion API Client")
    print("=" * 50)
    print("\nTo use this client:")
    print("1. Set environment variables:")
    print("   export GSM_FUSION_API_KEY='your-api-key'")
    print("   export GSM_FUSION_USERNAME='your-username'")
    print("   export GSM_FUSION_BASE_URL='https://hammerfusion.com'")
    print("\n2. Import and use:")
    print("   from gsm_fusion_client import GSMFusionClient")
    print("   client = GSMFusionClient()")
    print("   services = client.get_imei_services()")
