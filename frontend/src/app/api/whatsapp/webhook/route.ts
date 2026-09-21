import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'https://perseuskyogre-leagle.hf.space/api/whatsapp/webhook';

export async function POST(request: NextRequest) {
  try {
    // Get the raw form data from Twilio
    const formData = await request.formData();

    // Forward the request to the FastAPI backend
    const response = await fetch(BACKEND_URL, {
      method: 'POST',
      body: formData,
      headers: {
        // Remove Content-Type header to let fetch set it with proper boundary
        'Accept': 'application/json, text/plain, application/xml',
      },
    });

    // Get the response body
    const responseText = await response.text();

    // Return the response from backend to Twilio
    return new NextResponse(responseText, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'application/xml',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Webhook proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process webhook' },
      { status: 500 }
    );
  }
}

// Allow GET requests for webhook verification
export async function GET(request: NextRequest) {
  try {
    const response = await fetch(BACKEND_URL, {
      method: 'GET',
    });

    const responseText = await response.text();

    return new NextResponse(responseText, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'text/plain',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    console.error('Webhook GET error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
