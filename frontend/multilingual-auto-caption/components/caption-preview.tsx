"use client"

import { useMemo, useRef, useState, useEffect } from "react"
import { LANGUAGES } from "@/lib/languages"

// Reference video dimensions
const REFERENCE_WIDTH = 1920
const REFERENCE_HEIGHT = 1080

// Sample text translations for preview
const PREVIEW_TRANSLATIONS: Record<string, string> = {
  ab: "SQL аҵара ахә аҵоуп",
  af: "Daar is waarde in die leer en verstaan van SQL",
  am: "SQL መማር እና መረዳት ዋጋ አለው",
  ar: "هناك قيمة في تعلم وفهم SQL",
  as: "SQL শিকা আৰু বুজাত মূল্য আছে",
  az: "SQL öyrənmək və anlamaqda dəyər var",
  ba: "SQL өйрәнеүҙең һәм аңлауҙың ҡиммәте бар",
  be: "Ёсць каштоўнасць у вывучэнні і разуменні SQL",
  bg: "Има стойност в изучаването и разбирането на SQL",
  bn: "SQL শেখা এবং বোঝার মধ্যে মূল্য আছে",
  bo: "SQL སྦྱོང་བ་དང་རྟོགས་པར་རིན་ཐང་ཡོད།",
  br: "Bez a zo talvoudegezh en deskiñ ha kompren SQL",
  bs: "Postoji vrijednost u učenju i razumijevanju SQL-a",
  ca: "Hi ha valor en aprendre i entendre SQL",
  ceb: "Adunay bili sa pagkat-on ug pagsabot sa SQL",
  cs: "V učení a porozumění SQL je hodnota",
  cy: "Mae gwerth mewn dysgu a deall SQL",
  da: "Der er værdi i at lære og forstå SQL",
  de: "Es hat Wert, SQL zu lernen und zu verstehen",
  el: "Υπάρχει αξία στην εκμάθηση και κατανόηση της SQL",
  en: "There is value in learning and understanding SQL",
  eo: "Estas valoro lerni kaj kompreni SQL",
  es: "Hay valor en aprender y entender SQL",
  et: "SQL-i õppimisel ja mõistmisel on väärtus",
  eu: "SQL ikastea eta ulertzea baliotsua da",
  fa: "یادگیری و درک SQL ارزش دارد",
  fi: "SQL:n oppimisessa ja ymmärtämisessä on arvoa",
  fo: "Tað er virði í at læra og skilja SQL",
  fr: "Il y a de la valeur à apprendre et comprendre SQL",
  gl: "Hai valor en aprender e entender SQL",
  gn: "Oĩ valor SQL ñemoarandu ha oikuaápe",
  gu: "SQL શીખવામાં અને સમજવામાં મૂલ્ય છે",
  gv: "Ta feeuid ayns gynsaghey as toiggal SQL",
  ha: "Akwai daraja wajen koyon da fahimtar SQL",
  haw: "He waiwai ko ka aʻo ʻana a me ka hoʻomaopopo ʻana i ka SQL",
  hi: "SQL सीखने और समझने में मूल्य है",
  hr: "Postoji vrijednost u učenju i razumijevanju SQL-a",
  ht: "Gen valè nan aprann ak konprann SQL",
  hu: "Értékes az SQL tanulása és megértése",
  hy: "SQL-ը հասկանալը արժեք ունի",
  ia: "Il ha valor in apprender e comprender SQL",
  id: "Ada nilai dalam mempelajari dan memahami SQL",
  is: "Það er gildi í að læra og skilja SQL",
  it: "C'è valore nell'imparare e comprendere SQL",
  iw: "יש ערך בלמידה והבנה של SQL",
  ja: "SQLを学び理解することには価値がある",
  jw: "Ana regane sinau lan ngerti SQL",
  ka: "SQL-ის სწავლასა და გაგებაში ღირებულებაა",
  kk: "SQL үйрену мен түсінудің құндылығы бар",
  km: "មានតម្លៃក្នុងការរៀន និងយល់អំពី SQL",
  kn: "SQL ಕಲಿಯುವುದು ಮತ್ತು ಅರ್ಥಮಾಡಿಕೊಳ್ಳುವುದರಲ್ಲಿ ಮೌಲ್ಯವಿದೆ",
  ko: "SQL을 배우고 이해하는 데는 가치가 있습니다",
  la: "Valor est in discendo et intellegendo SQL",
  lb: "Et ass Wäert SQL ze léieren an ze verstoen",
  ln: "Ezali na motuya koyekola mpe kososola SQL",
  lo: "ມີຄຸນຄ່າໃນການຮຽນຮູ້ແລະເຂົ້າໃຈ SQL",
  lt: "SQL mokymasis ir supratimas turi vertę",
  lv: "SQL apgūšanā un izpratnē ir vērtība",
  mg: "Misy tombony ny fianarana sy fahatakarana ny SQL",
  mi: "He uara kei te ako me te mōhio ki te SQL",
  mk: "Има вредност во учењето и разбирањето на SQL",
  ml: "SQL പഠിക്കുന്നതിലും മനസ്സിലാക്കുന്നതിലും മൂല്യമുണ്ട്",
  mn: "SQL сурч, ойлгоход үнэ цэнэ байдаг",
  mr: "SQL शिकणे आणि समजून घेण्यात मूल्य आहे",
  ms: "Terdapat nilai dalam mempelajari dan memahami SQL",
  mt: "Hemm valur fit-tagħlim u l-fehim ta' SQL",
  my: "SQL သင်ယူခြင်းနှင့် နားလည်ခြင်းတွင် တန်ဖိုးရှိသည်",
  ne: "SQL सिक्न र बुझ्नमा मूल्य छ",
  nl: "Er is waarde in het leren en begrijpen van SQL",
  nn: "Det er verdi i å lære og forstå SQL",
  no: "Det er verdi i å lære og forstå SQL",
  oc: "I a de valor en apprendre e compròòner SQL",
  pa: "SQL ਸਿੱਖਣ ਅਤੇ ਸਮਝਣ ਵਿੱਚ ਮੁੱਲ ਹੈ",
  pl: "Jest wartość w nauce i zrozumieniu SQL",
  ps: "د SQL زده کړه او پوهیدل ارزښت لري",
  pt: "Há valor em aprender e entender SQL",
  ro: "Există valoare în a învăța și înțelege SQL",
  ru: "Есть ценность в изучении и понимании SQL",
  sa: "SQL अध्ययने अवबोधने च मूल्यं अस्ति",
  sco: "There is value in learnin an unnerstaundin SQL",
  sd: "SQL سکڻ ۽ سمجھڻ ۾ قدر آهي",
  si: "SQL ඉගෙනීම සහ තේරුම් ගැනීමේ වටිනාකමක් ඇත",
  sk: "V učení a pochopení SQL je hodnota",
  sl: "V učenju in razumevanju SQL je vrednost",
  sn: "Pane kukosha mukudzidza nekunzwisisa SQL",
  so: "Waxaa qiimo leh barashada iyo fahamka SQL",
  sq: "Ka vlerë të mësosh dhe të kuptosh SQL",
  sr: "Постоји вредност у учењу и разумевању SQL-а",
  su: "Aya ajén dina diajar sareng ngartos SQL",
  sv: "Det finns värde i att lära sig och förstå SQL",
  sw: "Kuna thamani katika kujifunza na kuelewa SQL",
  ta: "SQL கற்றல் மற்றும் புரிந்துகொள்வதில் மதிப்பு உள்ளது",
  te: "SQL నేర్చుకోవడం మరియు అర్థం చేసుకోవడంలో విలువ ఉంది",
  tg: "Омӯхтан ва фаҳмидани SQL арзиш дорад",
  th: "มีคุณค่าในการเรียนรู้และทำความเข้าใจ SQL",
  tk: "SQL öwrenmekde we düşünmekde baha bar",
  tl: "May halaga sa pag-aaral at pag-unawa ng SQL",
  tr: "SQL öğrenmenin ve anlamanın değeri var",
  tt: "SQL өйрәнү һәм аңлауның кыйммәте бар",
  uk: "Є цінність у вивченні та розумінні SQL",
  ur: "SQL سیکھنے اور سمجھنے میں قدر ہے",
  uz: "SQL o'rganish va tushunishda qiymat bor",
  vi: "Có giá trị trong việc học và hiểu SQL",
  war: "May bili ha pag-aram ngan pagsabot han SQL",
  yi: "עס איז ווערט אין לערנען און פארשטיין SQL",
  yo: "Iye wa ninu kikọ ati loye SQL",
  zh: "学习和理解SQL是有价值的",
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
