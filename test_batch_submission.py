"""
Test script to demonstrate batch vs individual submission
"""

# Simulate the performance difference

print("="*80)
print("PERFORMANCE COMPARISON: Individual vs Batch Submission")
print("="*80)

def calculate_time(num_imeis, imeis_per_call, workers, seconds_per_call):
    """Calculate processing time"""
    api_calls_needed = (num_imeis + imeis_per_call - 1) // imeis_per_call
    sequential_batches = (api_calls_needed + workers - 1) // workers
    total_seconds = sequential_batches * seconds_per_call
    return api_calls_needed, total_seconds

# Test with 20,000 IMEIs
num_imeis = 20000
workers = 30
avg_api_time = 5  # seconds per API call

print(f"\nProcessing {num_imeis:,} IMEIs with {workers} workers:\n")

# Individual submission (current)
calls1, time1 = calculate_time(num_imeis, 1, workers, avg_api_time)
print(f"Method 1: INDIVIDUAL (1 IMEI per call)")
print(f"  API Calls: {calls1:,}")
print(f"  Time: {time1:,} seconds = {time1/60:.1f} minutes = {time1/3600:.2f} hours")
print(f"  Status: ❌ TOO SLOW\n")

# Chunk of 10
calls2, time2 = calculate_time(num_imeis, 10, workers, avg_api_time)
print(f"Method 2: SMALL CHUNKS (10 IMEIs per call)")
print(f"  API Calls: {calls2:,}")
print(f"  Time: {time2:,} seconds = {time2/60:.1f} minutes")
print(f"  Improvement: {time1/time2:.1f}x faster")
print(f"  Status: ⚠️  BETTER\n")

# Chunk of 50
calls3, time3 = calculate_time(num_imeis, 50, workers, avg_api_time)
print(f"Method 3: MEDIUM CHUNKS (50 IMEIs per call)")
print(f"  API Calls: {calls3:,}")
print(f"  Time: {time3:,} seconds = {time3/60:.1f} minutes")
print(f"  Improvement: {time1/time3:.1f}x faster")
print(f"  Status: ✅ GOOD\n")

# Chunk of 100
calls4, time4 = calculate_time(num_imeis, 100, workers, avg_api_time)
print(f"Method 4: LARGE CHUNKS (100 IMEIs per call) ← RECOMMENDED")
print(f"  API Calls: {calls4:,}")
print(f"  Time: {time4:,} seconds = {time4/60:.1f} minutes")
print(f"  Improvement: {time1/time4:.1f}x faster")
print(f"  Status: ✅ EXCELLENT\n")

# Chunk of 500
calls5, time5 = calculate_time(num_imeis, 500, workers, avg_api_time)
print(f"Method 5: HUGE CHUNKS (500 IMEIs per call)")
print(f"  API Calls: {calls5:,}")
print(f"  Time: {time5:,} seconds = {time5/60:.1f} minutes")
print(f"  Improvement: {time1/time5:.1f}x faster")
print(f"  Status: ✅ BEST (if API supports it)\n")

print("="*80)
print("RECOMMENDATION:")
print("="*80)
print(f"Start with 100 IMEIs per call (Method 4)")
print(f"This gives you {time1/time4:.0f}x speedup with low risk of API errors")
print(f"\n20,000 IMEIs would take: {time4} seconds ({time4/60:.1f} minutes)")
print("="*80)
