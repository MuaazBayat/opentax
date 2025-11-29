# Zustand State Management

This project uses [Zustand](https://github.com/pmndrs/zustand) for state management with persistence and caching.

## Stores

### 1. Dashboard Store (`store/dashboardStore.ts`)

Manages dashboard state with smart caching to prevent unnecessary API calls.

**Features:**
- **Smart Caching**: Only fetches data when filters (date range, currency) change
- **Persistence**: Saves user's filter preferences to localStorage
- **Auto-fetch**: Automatically fetches new data when filters change

**State:**
- `summaryData`: API response with transactions, invoices, and daily breakdown
- `startDate`, `endDate`: Date range filters
- `currency`: Selected currency for conversion
- `viewMode`: 'count' or 'value' chart display mode
- `loading`, `error`: Loading and error states

**Actions:**
- `setStartDate(date)`: Update start date and fetch new data
- `setEndDate(date)`: Update end date and fetch new data
- `setCurrency(currency)`: Update currency and fetch new data
- `setViewMode(mode)`: Update view mode (no refetch)
- `fetchSummary()`: Manually trigger data fetch
- `clearCache()`: Clear cached data and refetch

**Usage:**
```typescript
import { useDashboardStore } from '../store/dashboardStore';

function Dashboard() {
  const {
    summaryData,
    startDate,
    currency,
    loading,
    setStartDate,
    setCurrency,
  } = useDashboardStore();

  // Data is automatically fetched when component mounts
  // and refetched when filters change
}
```

### 2. Chat Store (`store/chatStore.ts`)

Manages AI Assistant chat state with session persistence.

**Features:**
- **Message History**: Stores all messages in session
- **Session Persistence**: Chat history persists during browser session
- **Auto-loading**: Manages loading state automatically

**State:**
- `messages`: Array of user and assistant messages
- `loading`: Whether a message is being sent

**Actions:**
- `sendMessage(content)`: Send a message to AI assistant
- `clearMessages()`: Clear all chat messages

**Usage:**
```typescript
import { useChatStore } from '../../store/chatStore';

function Chat() {
  const { messages, loading, sendMessage, clearMessages } = useChatStore();

  const handleSend = () => {
    sendMessage('What are my total transactions?');
  };
}
```

## Benefits

### 1. **Performance**
- Cached data prevents redundant API calls
- Instant UI updates when changing view modes
- Smart cache invalidation only when needed

### 2. **User Experience**
- Filter preferences persist across page reloads
- Chat history preserved during session
- Fast interactions with cached data

### 3. **Developer Experience**
- Clean, predictable state management
- No prop drilling needed
- Easy to test and debug
- TypeScript support built-in

## Cache Strategy

### Dashboard Store
- **Storage**: localStorage (persists across sessions)
- **Cache Key**: `${startDate}_${endDate}_${currency}`
- **Invalidation**: Automatic when any filter changes
- **What's Cached**: Only user preferences (dates, currency, view mode)
- **What's Not Cached**: Actual API response data (always fetched fresh)

### Chat Store
- **Storage**: sessionStorage (cleared on tab close)
- **Persistence**: Chat history for current session only
- **Invalidation**: Manual via "Clear Chat" button

## Example Workflows

### Dashboard Data Flow
1. User opens dashboard → `fetchSummary()` called
2. Store checks cache key against current filters
3. If cache miss → Fetch from API
4. If cache hit → Use existing data
5. User changes date → New cache key → Fetch from API
6. User changes view mode → Same cache key → No fetch

### Chat Data Flow
1. User sends message → Add to messages array immediately
2. Store sets `loading: true`
3. API call to `/api/ai-assistant`
4. Response added to messages array
5. Store sets `loading: false`
6. All messages saved to sessionStorage

## Debugging

Enable Zustand DevTools in browser console:
```typescript
// In store file
import { devtools } from 'zustand/middleware';

create(devtools((set, get) => ({ ... })))
```

Or use Redux DevTools extension - Zustand is compatible!
