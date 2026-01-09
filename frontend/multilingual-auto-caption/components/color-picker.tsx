"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface ColorPickerProps {
  value: string
  onChange: (color: string) => void
}

export function ColorPicker({ value, onChange }: ColorPickerProps) {
  const [hue, setHue] = useState(0)
  const [saturation, setSaturation] = useState(0)
  const [lightness, setLightness] = useState(0)
  const [inputValue, setInputValue] = useState(value)
  const satLightRef = useRef<HTMLDivElement>(null)
  const hueRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const { h, s, l } = hexToHsl(value)
    setHue(h)
    setSaturation(s)
    setLightness(l)
    setInputValue(value)
  }, [value])

  function hexToHsl(hex: string): { h: number; s: number; l: number } {
    const r = Number.parseInt(hex.slice(1, 3), 16) / 255
    const g = Number.parseInt(hex.slice(3, 5), 16) / 255
    const b = Number.parseInt(hex.slice(5, 7), 16) / 255

    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h = 0
    let s = 0
    const l = (max + min) / 2

    if (max !== min) {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6
          break
        case g:
          h = ((b - r) / d + 2) / 6
          break
        case b:
          h = ((r - g) / d + 4) / 6
          break
      }
    }

    return { h: h * 360, s: s * 100, l: l * 100 }
  }

  function hslToHex(h: number, s: number, l: number): string {
    s /= 100
    l /= 100
    const a = s * Math.min(l, 1 - l)
    const f = (n: number) => {
      const k = (n + h / 30) % 12
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
      return Math.round(255 * color)
        .toString(16)
        .padStart(2, "0")
    }
    return `#${f(0)}${f(8)}${f(4)}`
  }

  const updateColor = (newHue: number, newSat: number, newLight: number) => {
    const hex = hslToHex(newHue, newSat, newLight)
    setHue(newHue)
    setSaturation(newSat)
    setLightness(newLight)
    setInputValue(hex)
    onChange(hex)
  }

  const handleSatLightMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!satLightRef.current) return
    const rect = satLightRef.current.getBoundingClientRect()
    const clientX = "touches" in e ? e.touches[0].clientX : e.clientX
    const clientY = "touches" in e ? e.touches[0].clientY : e.clientY
    const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
    const y = Math.max(0, Math.min(1, (clientY - rect.top) / rect.height))
    const newSat = x * 100
    const newLight = 100 - y * 100
    updateColor(hue, newSat, newLight)
  }

  const handleHueMove = (e: React.MouseEvent | React.TouchEvent) => {
    if (!hueRef.current) return
    const rect = hueRef.current.getBoundingClientRect()
    const clientX = "touches" in e ? e.touches[0].clientX : e.clientX
    const x = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width))
    const newHue = x * 360
    updateColor(newHue, saturation, lightness)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInputValue(newValue)
    if (/^#[0-9A-Fa-f]{6}$/.test(newValue)) {
      const { h, s, l } = hexToHsl(newValue)
      setHue(h)
      setSaturation(s)
      setLightness(l)
      onChange(newValue)
    }
  }

  return (
    <div className="space-y-3">
      <Label className="text-foreground">Caption Color</Label>
      <div className="flex gap-4 items-start">
        <div className="space-y-2 flex-1">
          {/* Saturation/Lightness picker */}
          <div
            ref={satLightRef}
            className="relative w-full h-32 rounded-lg cursor-crosshair border border-border"
            style={{
              background: `linear-gradient(to top, #000, transparent), linear-gradient(to right, #fff, hsl(${hue}, 100%, 50%))`,
            }}
            onMouseDown={(e) => {
              handleSatLightMove(e)
              const moveHandler = (ev: MouseEvent) => handleSatLightMove(ev as unknown as React.MouseEvent)
              const upHandler = () => {
                document.removeEventListener("mousemove", moveHandler)
                document.removeEventListener("mouseup", upHandler)
              }
              document.addEventListener("mousemove", moveHandler)
              document.addEventListener("mouseup", upHandler)
            }}
            onTouchStart={handleSatLightMove}
            onTouchMove={handleSatLightMove}
          >
            <div
              className="absolute w-4 h-4 border-2 border-foreground rounded-full -translate-x-1/2 -translate-y-1/2 pointer-events-none"
              style={{
                left: `${saturation}%`,
                top: `${100 - lightness}%`,
                backgroundColor: value,
              }}
            />
          </div>
          {/* Hue slider */}
          <div
            ref={hueRef}
            className="relative w-full h-4 rounded-full cursor-pointer"
            style={{
              background: "linear-gradient(to right, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000)",
            }}
            onMouseDown={(e) => {
              handleHueMove(e)
              const moveHandler = (ev: MouseEvent) => handleHueMove(ev as unknown as React.MouseEvent)
              const upHandler = () => {
                document.removeEventListener("mousemove", moveHandler)
                document.removeEventListener("mouseup", upHandler)
              }
              document.addEventListener("mousemove", moveHandler)
              document.addEventListener("mouseup", upHandler)
            }}
            onTouchStart={handleHueMove}
            onTouchMove={handleHueMove}
          >
            <div
              className="absolute w-4 h-4 border-2 border-foreground rounded-full -translate-x-1/2 top-0 pointer-events-none"
              style={{
                left: `${(hue / 360) * 100}%`,
                backgroundColor: `hsl(${hue}, 100%, 50%)`,
              }}
            />
          </div>
        </div>
        <div className="flex flex-col gap-2 items-center">
          <div className="w-12 h-12 rounded-lg border border-border" style={{ backgroundColor: value }} />
          <Input
            value={inputValue}
            onChange={handleInputChange}
            className="w-24 text-center font-mono text-sm bg-input text-foreground"
            placeholder="#000000"
          />
        </div>
      </div>
    </div>
  )
}
