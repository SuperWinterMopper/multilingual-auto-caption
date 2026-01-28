import type { CaptionOptions } from "./validation"

export const API_ROOT = "/api/py"

export interface UploadResponse {
  success: boolean
  videoUrl?: string
  downloadUrl?: string
  error?: string
}

export async function checkBackendHealth(): Promise<boolean> {
  console.log(`[Client] Checking backend health at ${API_ROOT}/health...`)
  try {
    const res = await fetch(`${API_ROOT}/health`)
    console.log(`[Client] Health check status: ${res.status}`)
    return res.ok
  } catch (err) {
    console.error("[Client] Health check failed:", err)
    return false
  }
}

export async function uploadVideo(file: File, options: CaptionOptions, email?: string): Promise<UploadResponse> {
  console.log(`[Client] Starting uploadVideo for file: ${file.name} (${file.size} bytes)`)
  console.log(`[Client] Options:`, options)

  try {
    const filename = encodeURIComponent(file.name)

    // 1) Request presigned upload URL from backend (GET)
    const presignedUrlEndpoint = `${API_ROOT}/presigned?filename=${filename}`
    console.log(`[Client] 1. Requesting presigned URL... GET ${presignedUrlEndpoint}`)
    
    const presignedRes = await fetch(presignedUrlEndpoint, {
      method: "GET",
    })

    if (!presignedRes.ok) {
      const text = await presignedRes.text()
      console.error(`[Client] Presigned request failed: ${presignedRes.status} ${text}`)
      return { success: false, error: `Presigned request failed: ${presignedRes.status} ${text}` }
    }
    
    // Parse response - expecting URL string or JSON
    let uploadUrl = ""
    const contentType = presignedRes.headers.get("content-type")
    if (contentType && contentType.includes("application/json")) {
        const presignedJson = await presignedRes.json()
        uploadUrl = presignedJson.upload_url || presignedJson.uploadUrl || presignedJson
    } else {
        uploadUrl = await presignedRes.text()
        uploadUrl = uploadUrl.replace(/^"|"$/g, '').trim() // Remove potential quotes
    }
    
    console.log(`[Client] Received upload URL (truncated): ${uploadUrl.substring(0, 50)}...`)

    if (!uploadUrl) {
       console.error("[Client] Presigned response was empty")
       return { success: false, error: "Presigned response did not include upload_url" }
    }

    // 2) Upload the file to the presigned URL (PUT)
    console.log(`[Client] 2. Uploading file to S3 presigned URL...`)
    const putRes = await fetch(uploadUrl, {
      method: "PUT",
      headers: {
        "Content-Type": file.type || "video/mp4",
      },
      body: file,
    })

    console.log(`[Client] Upload PUT response status: ${putRes.status}`)

    if (!putRes.ok) {
      const text = await putRes.text()
      console.error(`[Client] Upload failed: ${putRes.status} ${text}`)
      return { success: false, error: `Upload failed: ${putRes.status} ${text}` }
    }

    // 3) Notify backend to start captioning by posting to /caption
    console.log(`[Client] 3. Starting captioning job...`)
    
    // Construct payload with explicit snake_case keys for Python backend compatibility
    const snakeCasePayload = {
        upload_url: uploadUrl.split('?')[0], // Use clean URL if possible, or full URL if backend needs sign params
        caption_color: options.captionColor,
        font_size: options.fontSize,
        stroke_width: options.strokeWidth,
        convert_to: options.convertTo,
        explicit_langs: options.explicitLanguages || [],
        email: email
    }
    // Safety fallback: If backend expects full signed URL to download file using standard http client
    if (uploadUrl.includes("?")) {
        snakeCasePayload.upload_url = uploadUrl; 
    }
    
    console.log(`[Client] Caption Payload:`, snakeCasePayload)

    const captionRes = await fetch(`${API_ROOT}/caption`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(snakeCasePayload),
    })

    console.log(`[Client] Caption response status: ${captionRes.status}`)

    if (!captionRes.ok) {
      const text = await captionRes.text()
      console.error(`[Client] Caption request failed: ${captionRes.status} ${text}`)
      return { success: false, error: `Caption request failed: ${captionRes.status} ${text}` }
    }

    let captionJson: any = {}
    try { 
        captionJson = await captionRes.json() 
        console.log(`[Client] Caption JSON Response:`, captionJson)
    } catch (e) { 
        console.warn("[Client] Could not parse caption response JSON") 
    }

    const downloadUrl = captionJson.download_url || captionJson.downloadUrl || captionJson.download || undefined

    if (downloadUrl) {
        console.log(`[Client] Success! Download URL: ${downloadUrl}`)
        // If email was provided, we can trigger it here or let UI trigger it. 
        // Logic in UI: if (uploadResult.success && email) -> sendDownloadLinkEmail
        // So we just return success here.
    } else {
        console.warn(`[Client] Warning: No download URL found in response`)
    }

    return {
      success: true,
      videoUrl: URL.createObjectURL(file), 
      downloadUrl,
    }
  } catch (err: any) {
    console.error("[Client] Exception during uploadVideo:", err)
    return { success: false, error: String(err) }
  }
}

export function estimateProcessingTime(fileSizeMb: number, videoLengthSeconds: number): number {
  // Returns estimated time in minutes
  // Formula: file_size_mb * 0.2 + video_length_minutes * 2
  const videoLengthMinutes = videoLengthSeconds / 60
  const estimate = fileSizeMb * 0.2 + videoLengthMinutes * 2
  console.log(`[Client] Estimating time: Size=${fileSizeMb.toFixed(2)}MB, Length=${videoLengthSeconds}s -> Estimate=${estimate.toFixed(2)} min`)
  return estimate
}

export async function sendDownloadLinkEmail(email: string, downloadUrl: string): Promise<{ success: boolean; error?: string }> {
  console.log(`[Client] Sending download request to internal API for: ${email}`)
  try {
    const response = await fetch('/api/email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, downloadUrl })
    })
    
    const result = await response.json()
    console.log(`[Client] Email API Result:`, result)
    
    if (!response.ok || !result.success) {
       console.error(`[Client] Email API failed:`, result.error)
       return { success: false, error: result.error || "Failed to send email" }
    }
    
    return { success: true }
  } catch (error: any) {
    console.error("[Client] Failed to send email:", error)
    return { success: false, error: error.message || "Failed to send email" }
  }
}
