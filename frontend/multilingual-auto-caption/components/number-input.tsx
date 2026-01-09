"use client"

import type React from "react"
import { useState } from "react"

import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Minus, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"

interface NumberInputProps {
  label: string
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
}

export function NumberInput({ label, value, onChange, min = 0, max = 100, step = 1 }: NumberInputProps) {
  // Local state to allow free typing without immediate clamping
  const [localValue, setLocalValue] = useState<string>(String(value))
  const [isFocused, setIsFocused] = useState(false)

  const handleIncrement = () => {
    const newValue = Math.min(value + step, max)
    onChange(newValue)
    setLocalValue(String(newValue))
  }

  const handleDecrement = () => {
    const newValue = Math.max(value - step, min)
    onChange(newValue)
    setLocalValue(String(newValue))
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    setLocalValue(inputValue)
    
    // Only update parent if it's a valid number
    const newValue = Number.parseInt(inputValue, 10)
    if (!isNaN(newValue)) {
      onChange(newValue)
    }
  }

  const handleBlur = () => {
    setIsFocused(false)
    // On blur, clamp to valid range
    const numValue = Number.parseInt(localValue, 10)
    if (isNaN(numValue) || numValue < min) {
      onChange(min)
      setLocalValue(String(min))
    } else if (numValue > max) {
      onChange(max)
      setLocalValue(String(max))
    } else {
      setLocalValue(String(numValue))
    }
  }

  const handleFocus = () => {
    setIsFocused(true)
    setLocalValue(String(value))
  }

  // Sync local value with prop when not focused
  const displayValue = isFocused ? localValue : String(value)

  return (
    <div className="space-y-2">
      <Label className="text-foreground">{label}</Label>
      <div className="flex items-center gap-2">
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={handleDecrement}
          disabled={value <= min}
          className="bg-input border-border hover:bg-secondary text-foreground"
        >
          <Minus className="h-4 w-4" />
        </Button>
        <Input
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          value={displayValue}
          onChange={handleInputChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          className="w-20 text-center bg-input text-foreground border-border"
        />
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={handleIncrement}
          disabled={value >= max}
          className="bg-input border-border hover:bg-secondary text-foreground"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
