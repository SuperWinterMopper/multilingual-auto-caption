"use client"

import type React from "react"

import { useState, useRef, useCallback } from "react"
import { Upload, Loader2, Download, Video, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { uploadVideo, type UploadResponse } from "@/lib/upload-handler"
import { type CaptionOptions, validateCaptionOptions } from "@/lib/validation"
import { ColorPicker } from "./color-picker"
import { NumberInput } from "./number-input"
import { SingleLanguageSelector, MultiLanguageSelector } from "./language-selector"
import { CaptionPreview } from "./caption-preview"
import { cn } from "@/lib/utils"

export function VideoUploader() {
  const [options, setOptions] = useState<CaptionOptions>({
    captionColor: "#ffffff",
    fontSize: 48,
    strokeWidth: 4,
    convertTo: null,
    explicitLanguages: [],
  })

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = useCallback((file: File) => {
    if (!file.type.startsWith("video/")) {
      setErrors((prev) => ({
        ...prev,
        file: "Please select a valid video file",
      }))
      return
    }
    setSelectedFile(file)
    setErrors((prev) => {
      const { file: _, ...rest } = prev
      return rest
    })
    setUploadResult(null)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) {
        handleFileSelect(file)
      }
    },
    [handleFileSelect],
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleUpload = async () => {
    if (!selectedFile) return

    const validation = validateCaptionOptions(options)
    if (!validation.success) {
      const fieldErrors: Record<string, string> = {}
      validation.error.errors.forEach((err) => {
        const field = err.path[0] as string
        fieldErrors[field] = err.message
      })
      setErrors(fieldErrors)
      return
    }

    setIsUploading(true)
    setErrors({})

    try {
      const result = await uploadVideo(selectedFile, options)
      setUploadResult(result)
    } catch (error) {
      setUploadResult({
        success: false,
        error: "Failed to process video. Please try again.",
      })
    } finally {
      setIsUploading(false)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    setUploadResult(null)
    setErrors({})
  }

  if (isUploading) {
    return (
      <Card className="p-8 bg-card border-border">
        <div className="flex flex-col items-center justify-center gap-6 py-12">
          <div className="relative">
            <Loader2 className="h-16 w-16 animate-spin text-primary" />
            <div className="absolute inset-0 animate-pulse">
              <div className="h-16 w-16 rounded-full border-4 border-primary/30" />
            </div>
          </div>
          <div className="text-center space-y-2">
            <h3 className="text-xl font-semibold text-foreground">Processing your video...</h3>
            <p className="text-muted-foreground">Your processed video will be available in a few minutes</p>
          </div>
        </div>
      </Card>
    )
  }

  if (uploadResult?.success) {
    return (
      <Card className="p-8 bg-card border-border">
        <div className="flex flex-col items-center justify-center gap-6 py-12">
          <div className="h-16 w-16 rounded-full bg-primary/20 flex items-center justify-center">
            <Video className="h-8 w-8 text-primary" />
          </div>
          <div className="text-center space-y-2">
            <h3 className="text-xl font-semibold text-foreground">Video processed successfully!</h3>
            <p className="text-muted-foreground">Your captioned video is ready for download</p>
          </div>
          <div className="flex gap-4">
            <Button
              size="lg"
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={() => {
                if (uploadResult.videoUrl) {
                  const a = document.createElement("a")
                  a.href = uploadResult.videoUrl
                  a.download = "captioned-video.mp4"
                  a.click()
                }
              }}
            >
              <Download className="mr-2 h-5 w-5" />
              Download Video
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="border-border text-foreground hover:bg-secondary bg-transparent"
              onClick={resetForm}
            >
              Process Another
            </Button>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6 bg-card border-border">
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Upload Section */}
        <div className="space-y-6">
          <div
            className={cn(
              "border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer",
              isDragging ? "border-primary bg-primary/10" : "border-border hover:border-primary/50",
              selectedFile && "border-primary bg-primary/5",
            )}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFileSelect(file)
              }}
            />
            {selectedFile ? (
              <div className="space-y-3">
                <Video className="h-12 w-12 mx-auto text-primary" />
                <div>
                  <p className="font-medium text-foreground">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-foreground"
                  onClick={(e) => {
                    e.stopPropagation()
                    resetForm()
                  }}
                >
                  <X className="h-4 w-4 mr-1" />
                  Remove
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <Upload className="h-12 w-12 mx-auto text-muted-foreground" />
                <div>
                  <p className="font-medium text-foreground">Drop your video here or click to browse</p>
                  <p className="text-sm text-muted-foreground">Supports MP4, MOV, AVI, and more</p>
                </div>
              </div>
            )}
          </div>
          {errors.file && <p className="text-sm text-destructive">{errors.file}</p>}

          <Button
            size="lg"
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 text-lg py-6"
            onClick={handleUpload}
            disabled={!selectedFile}
          >
            <Upload className="mr-2 h-5 w-5" />
            Upload Video
          </Button>

              <CaptionPreview
                captionColor={options.captionColor}
                fontSize={options.fontSize}
                strokeWidth={options.strokeWidth}
                convertTo={options.convertTo}
              />
        </div>

        {/* Options Section */}
        <div className="space-y-6">
          <ColorPicker
            value={options.captionColor}
            onChange={(color) => setOptions((prev) => ({ ...prev, captionColor: color }))}
          />
          {errors.captionColor && <p className="text-sm text-destructive">{errors.captionColor}</p>}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <NumberInput
                label="Font Size"
                value={options.fontSize}
                onChange={(fontSize) => setOptions((prev) => ({ ...prev, fontSize }))}
                min={12}
                max={120}
              />
              {errors.fontSize && <p className="text-sm text-destructive mt-1">{errors.fontSize}</p>}
            </div>
            <div>
              <NumberInput
                label="Stroke Width"
                value={options.strokeWidth}
                onChange={(strokeWidth) => setOptions((prev) => ({ ...prev, strokeWidth }))}
                min={0}
                max={20}
              />
              {errors.strokeWidth && <p className="text-sm text-destructive mt-1">{errors.strokeWidth}</p>}
            </div>
          </div>

          <SingleLanguageSelector
            label="Convert to"
            value={options.convertTo}
            onChange={(convertTo) => setOptions((prev) => ({ ...prev, convertTo }))}
            note="Language of converted captions. If not set, captions will be in the spoken language."
          />

          <MultiLanguageSelector
            label="Provide explicit languages"
            value={options.explicitLanguages}
            onChange={(explicitLanguages) => setOptions((prev) => ({ ...prev, explicitLanguages }))}
            note="If spoken language detection is inaccurate, explicitly providing the spoken languages will restrict to classifying only from those provided."
          />

        </div>
      </div>
    </Card>
  )
}
