"use client"

import { useMemo, useRef, useState, useEffect } from "react"
import { LANGUAGES } from "@/lib/languages"

// Reference video dimensions
const REFERENCE_WIDTH = 1920
const REFERENCE_HEIGHT = 1080

// Sample text translations for preview
const PREVIEW_TRANSLATIONS: Record<string, string> = {
  en: "There is value in learning and understanding SQL",
  es: "Hay valor en aprender y entender SQL",
  fr: "Il y a de la valeur à apprendre et comprendre SQL",
  de: "Es hat Wert, SQL zu lernen und zu verstehen",
  it: "C'è valore nell'imparare e comprendere SQL",
  pt: "Há valor em aprender e entender SQL",
  ru: "Есть ценность в изучении и понимании SQL",
  zh: "学习和理解SQL是有价值的",
  ja: "SQLを学び理解することには価値がある",
  ko: "SQL을 배우고 이해하는 데는 가치가 있습니다",
  ar: "هناك قيمة في تعلم وفهم SQL",
  hi: "SQL सीखने और समझने में मूल्य है",
  bn: "SQL শেখা এবং বোঝার মধ্যে মূল্য আছে",
  pa: "SQL ਸਿੱਖਣ ਅਤੇ ਸਮਝਣ ਵਿੱਚ ਮੁੱਲ ਹੈ",
  vi: "Có giá trị trong việc học và hiểu SQL",
  th: "มีคุณค่าในการเรียนรู้และทำความเข้าใจ SQL",
  id: "Ada nilai dalam mempelajari dan memahami SQL",
  ms: "Terdapat nilai dalam mempelajari dan memahami SQL",
  tr: "SQL öğrenmenin ve anlamanın değeri var",
  pl: "Jest wartość w nauce i zrozumieniu SQL",
  uk: "Є цінність у вивченні та розумінні SQL",
  nl: "Er is waarde in het leren en begrijpen van SQL",
  sv: "Det finns värde i att lära sig och förstå SQL",
  da: "Der er værdi i at lære og forstå SQL",
  no: "Det er verdi i å lære og forstå SQL",
  fi: "SQL:n oppimisessa ja ymmärtämisessä on arvoa",
  el: "Υπάρχει αξία στην εκμάθηση και κατανόηση της SQL",
  he: "יש ערך בלמידה והבנה של SQL",
  cs: "V učení a porozumění SQL je hodnota",
  ro: "Există valoare în a învăța și înțelege SQL",
}

interface CaptionPreviewProps {
  captionColor: string
  fontSize: number
  strokeWidth: number
  convertTo: string | null
}

export function CaptionPreview({
  captionColor,
  fontSize,
  strokeWidth,
  convertTo,
}: CaptionPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [containerWidth, setContainerWidth] = useState(0)

  // Track container size for proportional scaling
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth)
      }
    }

    updateSize()
    
    const resizeObserver = new ResizeObserver(updateSize)
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current)
    }

    return () => resizeObserver.disconnect()
  }, [])

  // Get the text based on convertTo language
  const displayText = useMemo(() => {
    if (convertTo && PREVIEW_TRANSLATIONS[convertTo]) {
      return PREVIEW_TRANSLATIONS[convertTo]
    }
    // Default to English if no conversion or language not found
    return PREVIEW_TRANSLATIONS.en
  }, [convertTo])

  // Calculate the scale factor: how much smaller the preview is compared to reference
  const scaleFactor = containerWidth / REFERENCE_WIDTH

  // Calculate actual pixel values for the preview based on scale
  const scaledFontSize = fontSize * scaleFactor
  const scaledStrokeWidth = strokeWidth * scaleFactor

  // Calculate approximate text width at reference size
  // Average character width is roughly 0.55 * fontSize for Arial Bold
  const avgCharWidthAtReference = fontSize * 0.55
  
  // Max width is 90% of reference width
  const maxTextWidthAtReference = REFERENCE_WIDTH * 0.9
  
  // Split text into lines if needed (calculated at reference size)
  const wrappedLines = useMemo(() => {
    const words = displayText.split(' ')
    const lines: string[] = []
    let currentLine = ''
    
    for (const word of words) {
      const testLine = currentLine ? `${currentLine} ${word}` : word
      const testWidth = testLine.length * avgCharWidthAtReference
      
      if (testWidth > maxTextWidthAtReference && currentLine) {
        lines.push(currentLine)
        currentLine = word
      } else {
        currentLine = testLine
      }
    }
    
    if (currentLine) {
      lines.push(currentLine)
    }
    
    return lines
  }, [displayText, avgCharWidthAtReference, maxTextWidthAtReference])

  // Get language name for display
  const languageName = useMemo(() => {
    if (convertTo) {
      const lang = LANGUAGES.find(l => l.code === convertTo)
      return lang?.name || "English"
    }
    return "English"
  }, [convertTo])

  // Calculate smooth stroke shadow for better visibility
  // Using many small shadows in a circle pattern for smooth edges
  const strokeShadow = useMemo(() => {
    const s = scaledStrokeWidth
    if (s <= 0) return 'none'
    
    // Create smooth outline with many shadow layers
    const shadows: string[] = []
    const steps = 16 // Number of shadow directions for smoothness
    
    for (let i = 0; i < steps; i++) {
      const angle = (i / steps) * Math.PI * 2
      const x = Math.cos(angle) * s
      const y = Math.sin(angle) * s
      shadows.push(`${x.toFixed(2)}px ${y.toFixed(2)}px 0 #000`)
    }
    
    // Add a subtle blur shadow for extra smoothness
    shadows.push(`0 0 ${s * 0.5}px #000`)
    
    return shadows.join(', ')
  }, [scaledStrokeWidth])

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-foreground">Caption Preview (Note: approximation)</h3>
        <span className="text-xs text-muted-foreground">
          Reference: {REFERENCE_WIDTH}×{REFERENCE_HEIGHT}
        </span>
      </div>
      
      <div 
        ref={containerRef}
        className="relative w-full overflow-hidden rounded-lg border border-border bg-black"
        style={{ aspectRatio: `${REFERENCE_WIDTH} / ${REFERENCE_HEIGHT}` }}
      >
        {/* Background Image */}
        <img
          src="/lex.png"
          alt="Preview background"
          className="absolute inset-0 w-full h-full object-cover"
          draggable={false}
        />
        
        {/* Caption Overlay - positioned at bottom center */}
        {containerWidth > 0 && (
          <div 
            className="absolute left-0 right-0 flex flex-col items-center pointer-events-none"
            style={{ 
              bottom: `${50 * scaleFactor}px`,
            }}
          >
            {wrappedLines.map((line, index) => (
              <div
                key={index}
                style={{
                  fontSize: `${scaledFontSize}px`,
                  fontWeight: 700,
                  fontFamily: 'Arial, sans-serif',
                  lineHeight: 1.3,
                  color: captionColor,
                  textShadow: strokeShadow,
                  whiteSpace: 'pre',
                  textAlign: 'center',
                }}
              >
                {line}
              </div>
            ))}
          </div>
        )}
        
        {/* Language indicator badge */}
        <div 
          className="absolute bg-black/70 text-white rounded pointer-events-none"
          style={{
            top: `${8 * scaleFactor}px`,
            right: `${8 * scaleFactor}px`,
            fontSize: `${Math.max(10, 12 * scaleFactor)}px`,
            padding: `${Math.max(2, 4 * scaleFactor)}px ${Math.max(4, 8 * scaleFactor)}px`,
          }}
        >
          {languageName}
        </div>
      </div>
      
      <p className="text-xs text-muted-foreground text-center">
        Font: {fontSize}px | Stroke: {strokeWidth}px | Color: {captionColor}
      </p>
    </div>
  )
}
