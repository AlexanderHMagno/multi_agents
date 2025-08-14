# Real-Time Campaign Monitoring Features

This document describes the new real-time monitoring capabilities added to the Multi-Agent Campaign Generation API.

## Overview

The backend now provides real-time updates during campaign generation, allowing clients to monitor progress, track agent interactions, and get detailed workflow step information as the campaign is being generated.

## Key Features

### 1. Real-Time Progress Tracking
- **Endpoint**: `GET /api/v1/campaigns/{campaign_id}/progress`
- **Description**: Provides current progress, step information, and recent agent interactions
- **Updates**: Real-time progress updates as each workflow step completes

### 2. Live Streaming Updates
- **Endpoint**: `GET /api/v1/campaigns/{campaign_id}/stream`
- **Description**: Server-Sent Events (SSE) stream for live campaign updates
- **Features**: Real-time notifications for progress changes, agent interactions, and completion

### 3. Detailed Workflow Steps
- **Endpoint**: `GET /api/v1/campaigns/{campaign_id}/workflow-steps`
- **Description**: Comprehensive information about all workflow steps and their status
- **Data**: Step-by-step breakdown with completion status, artifacts generated, and performance metrics

## How It Works

### Workflow Execution
Instead of executing the entire workflow in a single call, the system now:

1. **Step-by-Step Execution**: Runs each agent sequentially with real-time updates
2. **Progress Tracking**: Updates progress after each step completion
3. **Agent Interaction Logging**: Records all agent activities and results
4. **State Management**: Maintains workflow state across steps

### Real-Time Updates
- **Progress Updates**: Sent after each workflow step completion
- **Agent Interactions**: Logged in real-time as agents execute
- **Status Changes**: Immediate notification of workflow state changes
- **Error Handling**: Real-time error reporting and recovery

## API Endpoints

### Progress Endpoint
```http
GET /api/v1/campaigns/{campaign_id}/progress
Authorization: Bearer {token}
```

**Response**:
```json
{
  "campaign_id": "campaign_20241201_120000_123456",
  "status": "running",
  "progress": {
    "step": "strategy",
    "step_name": "Strategy Team",
    "step_description": "Developing campaign strategy and positioning",
    "completed_steps": 2,
    "total_steps": 17,
    "progress_percentage": 12
  },
  "agent_interactions": [...],
  "artifacts_summary": {...},
  "estimated_completion": "About 15 minutes",
  "workflow_health": {...}
}
```

### Streaming Endpoint
```http
GET /api/v1/campaigns/{campaign_id}/stream
Authorization: Bearer {token}
```

**Response**: Server-Sent Events stream with real-time updates

### Workflow Steps Endpoint
```http
GET /api/v1/campaigns/{campaign_id}/workflow-steps
Authorization: Bearer {token}
```

**Response**: Detailed information about all workflow steps and their current status

## Workflow Steps

The system tracks 17 distinct workflow steps:

1. **Project Manager** - Initialize project and objectives
2. **Strategy Team** - Develop campaign strategy
3. **Audience Persona** - Create audience personas
4. **Creative Team** - Generate creative concepts
5. **Copy Team** - Write compelling copy
6. **CTA Optimizer** - Optimize calls-to-action
7. **Visual Team** - Create visual concepts
8. **Designer Team** - Design visual assets
9. **Social Media Campaign** - Develop social media strategy
10. **Emotion Personalization** - Add emotional intelligence
11. **Media Planner** - Plan media strategy
12. **Review Team** - Quality review and validation
13. **Campaign Summary** - Create campaign summary
14. **Client Summary** - Generate client-facing summary
15. **Web Developer** - Build campaign website
16. **HTML Validation** - Validate website code

## Client Implementation

### JavaScript Example (Progress Polling)
```javascript
async function monitorCampaign(campaignId, token) {
  const headers = { Authorization: `Bearer ${token}` };
  
  while (true) {
    try {
      const response = await fetch(`/api/v1/campaigns/${campaignId}/progress`, { headers });
      const progress = await response.json();
      
      // Update UI with progress
      updateProgressUI(progress);
      
      // Check if completed
      if (progress.status === 'completed' || progress.status === 'failed') {
        break;
      }
      
      // Wait before next check
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (error) {
      console.error('Error monitoring progress:', error);
      break;
    }
  }
}
```

### JavaScript Example (Server-Sent Events)
```javascript
function streamCampaignUpdates(campaignId, token) {
  const eventSource = new EventSource(`/api/v1/campaigns/${campaignId}/stream`);
  
  eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch (data.type) {
      case 'progress':
        updateProgressUI(data.progress);
        break;
      case 'completion':
        handleCompletion(data);
        eventSource.close();
        break;
      case 'error':
        handleError(data);
        eventSource.close();
        break;
    }
  };
  
  eventSource.onerror = function(error) {
    console.error('SSE error:', error);
    eventSource.close();
  };
}
```

## Testing

Use the provided test script to verify real-time functionality:

```bash
cd backend
python test_realtime_updates.py
```

This script will:
1. Create a test campaign
2. Monitor progress in real-time
3. Test all new endpoints
4. Display real-time updates

## Benefits

### For Users
- **Real-Time Visibility**: See exactly what's happening during campaign generation
- **Progress Tracking**: Know how much work remains and estimated completion time
- **Transparency**: Understand which agents are working and what they're doing
- **Better UX**: No more waiting without knowing what's happening

### For Developers
- **Debugging**: Real-time insight into workflow execution
- **Monitoring**: Track performance and identify bottlenecks
- **Integration**: Easy to build real-time dashboards and monitoring tools
- **Reliability**: Better error handling and recovery mechanisms

## Performance Considerations

- **Minimal Overhead**: Real-time updates add minimal processing overhead
- **Efficient Polling**: Progress endpoint optimized for frequent requests
- **Streaming**: SSE provides real-time updates without polling overhead
- **Caching**: Progress data cached to reduce database queries

## Future Enhancements

- **WebSocket Support**: Alternative to SSE for bi-directional communication
- **Progress Persistence**: Store progress data in database for historical analysis
- **Advanced Analytics**: Performance metrics and optimization suggestions
- **Real-Time Collaboration**: Multiple users monitoring the same campaign 