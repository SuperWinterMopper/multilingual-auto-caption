// Mirroring backend/src/dataclasses/inputs/caption.py
export interface CaptionInput {
  upload_url: string
  caption_color?: string
  font_size?: number
  stroke_width?: number
  convert_to?: string
  explicit_langs?: string[]
}

// Mirroring backend/src/dataclasses/inputs/presigned.py
export interface PresignedInput {
  filename: string
}
