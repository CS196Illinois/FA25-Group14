# AI Assistant Integration - Gemini API

## Overview

The AI Assistant feature uses Google's Gemini AI to provide personalized course recommendations based on student input.

## Setup

### 1. Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Add to Environment Variables

Add your API key to `.env`:

```bash
GEMINI_API_KEY=your-actual-api-key-here
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## How It Works

### Frontend (JavaScript)

- User fills out the AI form with:
  - Major/pathway
  - Goals and interests
  - Priority checkboxes (Gen Eds, balance workload, seek challenges)
- Form submission triggers async POST request to `/api/ai-assistant`
- Loading spinner displays while waiting for response
- AI recommendation is formatted and displayed with proper styling

### Backend (Python/Flask)

- Route: `POST /api/ai-assistant`
- Receives form data as JSON
- Builds a contextual prompt including:
  - Student's major and goals
  - Selected priorities
  - Sample course data for context
- Calls Gemini API using `google-generativeai` SDK
- Returns formatted recommendation

## API Endpoint

**POST** `/api/ai-assistant`

### Request Body

```json
{
  "major": "CS + Advertising minor",
  "goals": "Want to explore UI/UX design while completing gen eds",
  "priorities": ["gened", "balance"]
}
```

### Response

```json
{
  "success": true,
  "recommendation": "Detailed AI-generated course recommendations..."
}
```

### Error Response

```json
{
  "error": "Error message describing what went wrong"
}
```

## Features

✅ Real-time AI-powered course recommendations
✅ Context-aware suggestions based on available courses
✅ Personalized to student's major, goals, and priorities
✅ Formatted output with sections and bullet points
✅ Loading states and error handling
✅ Smooth scrolling to results
✅ Mobile-responsive design

## Security

- API key stored in environment variables (never committed)
- Rate limiting recommended for production
- Input validation on both frontend and backend
- Error messages don't expose sensitive information

## Limitations

- Course context limited to 50 courses to avoid token limits
- Gemini API has rate limits (check your quota)
- Responses may vary based on AI model updates
- Requires active internet connection

## Future Enhancements

- Cache common queries to reduce API calls
- Add more course context (majors, prerequisites, etc.)
- Include real review data in recommendations
- Save user preferences for better personalization
- Implement conversation history for follow-up questions
