"use client"

import { Check, ChevronsUpDown, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { LANGUAGES } from "@/lib/languages"
import { useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"

interface SingleLanguageSelectorProps {
  value: string | null
  onChange: (value: string | null) => void
  label: string
  placeholder?: string
  note: string
}

export function SingleLanguageSelector({
  value,
  onChange,
  label,
  placeholder = "Select language...",
  note,
}: SingleLanguageSelectorProps) {
  const [open, setOpen] = useState(false)

  const selectedLanguage = value ? LANGUAGES.find((lang) => lang.code === value) : null

  return (
    <div className="space-y-2">
      <Label className="text-foreground">{label}</Label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between bg-input text-foreground border-border hover:bg-secondary"
          >
            {selectedLanguage ? selectedLanguage.name : "None (caption stays in original language)"}
            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-full p-0 bg-popover border-border">
          <Command className="bg-transparent">
            <CommandInput placeholder={placeholder} className="text-foreground" />
            <CommandList>
              <CommandEmpty>No language found.</CommandEmpty>
              <CommandGroup>
                <CommandItem
                  value="none"
                  onSelect={() => {
                    onChange(null)
                    setOpen(false)
                  }}
                  className="text-foreground hover:bg-secondary"
                >
                  <Check className={cn("mr-2 h-4 w-4", value === null ? "opacity-100" : "opacity-0")} />
                  None (caption stays in original language)
                </CommandItem>
                {LANGUAGES.map((language) => (
                  <CommandItem
                    key={language.code}
                    value={language.name}
                    onSelect={() => {
                      onChange(language.code)
                      setOpen(false)
                    }}
                    className="text-foreground hover:bg-secondary"
                  >
                    <Check className={cn("mr-2 h-4 w-4", value === language.code ? "opacity-100" : "opacity-0")} />
                    {language.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
      {note && <p className="text-xs text-muted-foreground">{note}</p>}
    </div>
  )
}

interface MultiLanguageSelectorProps {
  value: string[]
  onChange: (value: string[]) => void
  label: string
  placeholder?: string
  note?: string
}

export function MultiLanguageSelector({
  value,
  onChange,
  label,
  placeholder = "Add languages...",
  note,
}: MultiLanguageSelectorProps) {
  const [open, setOpen] = useState(false)

  const selectedLanguages = LANGUAGES.filter((lang) => value.includes(lang.code))

  const removeLanguage = (code: string) => {
    onChange(value.filter((c) => c !== code))
  }

  return (
    <div className="space-y-2">
      <Label className="text-foreground">{label}</Label>
      <div className="space-y-2">
        {selectedLanguages.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {selectedLanguages.map((lang) => (
              <Badge
                key={lang.code}
                variant="secondary"
                className="bg-primary/20 text-primary border-primary/30 hover:bg-primary/30"
              >
                {lang.name}
                <button className="ml-1 hover:text-foreground" onClick={() => removeLanguage(lang.code)}>
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-full justify-between bg-input text-foreground border-border hover:bg-secondary"
            >
              {placeholder}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-full p-0 bg-popover border-border">
            <Command className="bg-transparent">
              <CommandInput placeholder="Search languages..." className="text-foreground" />
              <CommandList>
                <CommandEmpty>No language found.</CommandEmpty>
                <ScrollArea className="h-[200px]">
                  <CommandGroup>
                    {LANGUAGES.map((language) => (
                      <CommandItem
                        key={language.code}
                        value={language.name}
                        onSelect={() => {
                          if (value.includes(language.code)) {
                            onChange(value.filter((c) => c !== language.code))
                          } else {
                            onChange([...value, language.code])
                          }
                        }}
                        className="text-foreground hover:bg-secondary"
                      >
                        <Check
                          className={cn("mr-2 h-4 w-4", value.includes(language.code) ? "opacity-100" : "opacity-0")}
                        />
                        {language.name}
                      </CommandItem>
                    ))}
                  </CommandGroup>
                </ScrollArea>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>
      {note && <p className="text-xs text-muted-foreground">{note}</p>}
    </div>
  )
}
