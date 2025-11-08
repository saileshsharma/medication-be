# Mobile App Integration Guide

Step-by-step guide to integrate the Pixel Pirates backend with your React Native mobile app.

## Prerequisites

- ✅ Backend running (see QUICKSTART.md)
- ✅ React Native app from `pixel-pirates-app/`

## Step 1: Update Mock Data Service

Replace the mock scanning function with real API calls.

### Create API Service

Create `pixel-pirates-app/src/services/api.ts`:

```typescript
import { ScanResult } from '../context/ScanContext';

const API_BASE_URL = __DEV__
  ? Platform.select({
      ios: 'http://localhost:8000/api/v1',
      android: 'http://10.0.2.2:8000/api/v1',
    })
  : 'https://your-production-api.com/api/v1';

export const analyzeContent = async (text: string, sourceApp: string = 'Camera Scanner'): Promise<ScanResult> => {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: text,
        content_type: 'text',
        source_app: sourceApp,
        user_id_hash: await getUserIdHash(), // Implement this
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    // Transform API response to match ScanResult interface
    return {
      id: data.id,
      content: data.content,
      contentType: data.content_type,
      verdict: data.verdict,
      credibilityScore: data.credibility_score,
      timestamp: data.timestamp,
      sourceApp: data.source_app,
      sources: data.sources.map((source: any) => ({
        name: source.name,
        url: source.url,
        credibilityRating: source.credibility_rating,
      })),
      explanation: {
        summary: data.explanation.summary,
        reasons: data.explanation.reasons,
      },
    };
  } catch (error) {
    console.error('Analysis failed:', error);
    throw error;
  }
};

// Helper to get/create hashed user ID
const getUserIdHash = async (): Promise<string> => {
  const AsyncStorage = require('@react-native-async-storage/async-storage').default;
  let userId = await AsyncStorage.getItem('user_id_hash');

  if (!userId) {
    // Generate random ID and hash it
    userId = generateRandomHash();
    await AsyncStorage.setItem('user_id_hash', userId);
  }

  return userId;
};

const generateRandomHash = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};
```

## Step 2: Update Camera Scanner Screen

Replace mock scan with real API call in `CameraScannerScreen.tsx`:

```typescript
import { analyzeContent } from '../services/api';

const CameraScannerScreen = () => {
  // ... existing code ...

  const handleScan = async () => {
    if (!text.trim()) {
      Alert.alert('Error', 'Please enter some text to scan');
      return;
    }

    setScanning(true);

    try {
      // Call real API instead of simulateScan
      const result = await analyzeContent(text, 'Camera Scanner');

      // Add to history (existing code)
      addScan(result);

      // Show results modal (existing code)
      setScanResult(result);
      setResultModalVisible(true);

    } catch (error) {
      Alert.alert(
        'Scan Failed',
        'Unable to analyze content. Please check your connection and try again.'
      );
      console.error(error);
    } finally {
      setScanning(false);
    }
  };

  // ... rest of component ...
};
```

## Step 3: Add Error Handling & Loading States

Enhance user experience with proper error handling:

```typescript
import { useState, useEffect } from 'react';

const useApiCall = <T,>(apiFunction: () => Promise<T>) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiFunction();
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
};

// Usage in component
const { loading, error, execute } = useApiCall(() => analyzeContent(text));

const handleScan = async () => {
  try {
    const result = await execute();
    // Handle success
  } catch {
    // Error already set in state
    Alert.alert('Error', error || 'Something went wrong');
  }
};
```

## Step 4: Add Network Status Check

Detect offline mode and handle gracefully:

```typescript
import NetInfo from '@react-native-community/netinfo';

const checkConnection = async (): Promise<boolean> => {
  const state = await NetInfo.fetch();
  return state.isConnected ?? false;
};

const handleScan = async () => {
  // Check connection first
  const isConnected = await checkConnection();

  if (!isConnected) {
    Alert.alert(
      'No Connection',
      'You need an internet connection to scan content. Results will be cached for offline viewing.',
      [{ text: 'OK' }]
    );
    return;
  }

  // Proceed with scan...
};
```

## Step 5: Implement Caching

Add offline support with local caching:

```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_PREFIX = 'scan_cache_';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

const getCachedScan = async (contentHash: string): Promise<ScanResult | null> => {
  try {
    const cached = await AsyncStorage.getItem(`${CACHE_PREFIX}${contentHash}`);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      // Check if cache is still valid
      if (Date.now() - timestamp < CACHE_DURATION) {
        return data;
      }
    }
  } catch (error) {
    console.error('Cache read error:', error);
  }
  return null;
};

const cacheScan = async (contentHash: string, result: ScanResult) => {
  try {
    await AsyncStorage.setItem(
      `${CACHE_PREFIX}${contentHash}`,
      JSON.stringify({
        data: result,
        timestamp: Date.now(),
      })
    );
  } catch (error) {
    console.error('Cache write error:', error);
  }
};

// Updated analyzeContent with caching
export const analyzeContentWithCache = async (text: string): Promise<ScanResult> => {
  // Generate content hash
  const hash = simpleHash(text);

  // Check cache first
  const cached = await getCachedScan(hash);
  if (cached) {
    console.log('Using cached result');
    return cached;
  }

  // Call API
  const result = await analyzeContent(text);

  // Cache result
  await cacheScan(hash, result);

  return result;
};

const simpleHash = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(36);
};
```

## Step 6: Update Stats Screen

Fetch real statistics from backend:

```typescript
// Add to api.ts
export const getUserStats = async (days: number = 30) => {
  const userId = await getUserIdHash();
  const response = await fetch(
    `${API_BASE_URL}/stats?user_id_hash=${userId}&days=${days}`
  );
  return response.json();
};

// In StatsScreen.tsx
useEffect(() => {
  const fetchStats = async () => {
    try {
      const stats = await getUserStats(7); // Last 7 days
      setTotalScans(stats.total_scans);
      setVerifiedCount(stats.verified_count);
      setFakeCount(stats.fake_count);
      setProtectionScore(stats.average_credibility_score);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  fetchStats();
}, []);
```

## Step 7: Add Retry Logic

Handle temporary failures gracefully:

```typescript
const retryWithBackoff = async <T,>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      // Exponential backoff
      const waitTime = delay * Math.pow(2, i);
      console.log(`Retry ${i + 1}/${maxRetries} after ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  throw new Error('Max retries exceeded');
};

// Usage
const result = await retryWithBackoff(() => analyzeContent(text));
```

## Step 8: Testing the Integration

### 1. Start Backend

```bash
cd pixel-pirates-backend
docker-compose up -d
```

### 2. Update App Config

For **iOS Simulator**:
```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

For **Android Emulator**:
```typescript
const API_BASE_URL = 'http://10.0.2.2:8000/api/v1';
```

For **Physical Device**:
```typescript
// Find your computer's IP: ifconfig (Mac) or ipconfig (Windows)
const API_BASE_URL = 'http://192.168.1.XXX:8000/api/v1';
```

### 3. Test the Flow

1. Open the app
2. Go to Camera Scanner
3. Enter text: "Breaking news about climate change"
4. Tap Scan
5. Verify you get real analysis results

### 4. Check Backend Logs

```bash
docker-compose logs -f backend
```

You should see:
```
POST /api/v1/analyze 200 OK (234ms)
```

## Step 9: Production Deployment

### Backend Deployment

Deploy backend to cloud provider (AWS, GCP, Heroku, etc.):

```bash
# Example: Deploy to Heroku
heroku create pixelpirates-api
git push heroku main
```

### Update Mobile App

```typescript
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000/api/v1'
  : 'https://pixelpirates-api.herokuapp.com/api/v1';
```

### Environment Variables

Create `.env` in mobile app:
```
API_BASE_URL=https://your-api.com/api/v1
```

Install react-native-dotenv:
```bash
npm install react-native-dotenv
```

Use in code:
```typescript
import { API_BASE_URL } from '@env';
```

## Common Issues

### Issue: Connection Refused

**Solution:** Check IP address and port
```typescript
// iOS Simulator
'http://localhost:8000/api/v1'

// Android Emulator
'http://10.0.2.2:8000/api/v1'

// Physical device - use computer's IP
'http://192.168.1.5:8000/api/v1'  // Your actual IP
```

### Issue: CORS Error

**Solution:** Backend already configured for CORS. If issue persists, add your device IP to `.env`:
```
CORS_ORIGINS=http://localhost:3000,http://192.168.1.5:19000
```

### Issue: Slow Response

**Solutions:**
1. Check backend logs for errors
2. Verify database connection
3. Enable caching in app
4. Reduce network requests

### Issue: App Works in Dev but Not Production

**Solution:** Update API URL for production:
```typescript
const API_BASE_URL = __DEV__
  ? Platform.select({...})
  : Config.API_BASE_URL;  // From app config
```

## Performance Optimization

### 1. Request Batching

```typescript
const pendingScans: string[] = [];
let batchTimeout: NodeJS.Timeout;

const batchScan = (text: string) => {
  pendingScans.push(text);

  clearTimeout(batchTimeout);
  batchTimeout = setTimeout(async () => {
    // Send all pending scans in one request
    const results = await analyzeBatch(pendingScans);
    // Handle results
    pendingScans.length = 0;
  }, 500);
};
```

### 2. Response Caching

Cache API responses for 1 hour:
```typescript
const cache = new Map<string, { result: ScanResult; timestamp: number }>();

const getCached = (hash: string) => {
  const cached = cache.get(hash);
  if (cached && Date.now() - cached.timestamp < 3600000) {
    return cached.result;
  }
  return null;
};
```

## Monitoring

### Track API Performance

```typescript
const trackAPICall = async (endpoint: string, fn: () => Promise<any>) => {
  const start = Date.now();

  try {
    const result = await fn();
    const duration = Date.now() - start;

    // Log to analytics
    Analytics.track('api_call_success', {
      endpoint,
      duration,
    });

    return result;
  } catch (error) {
    Analytics.track('api_call_error', {
      endpoint,
      error: error.message,
    });
    throw error;
  }
};
```

## Next Steps

1. ✅ Backend integrated
2. ✅ Error handling added
3. ✅ Caching implemented
4. 🚀 Deploy to production
5. 📊 Add analytics
6. 🧪 Add E2E tests

---

**Need Help?**
- Backend API Docs: http://localhost:8000/docs
- Backend README: pixel-pirates-backend/README.md
- API Examples: pixel-pirates-backend/API_EXAMPLES.md
