import { z } from "zod"

export const captionOptionsSchema = z.object({
  captionColor: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Invalid hex color format")
    .default("#000000"),
  fontSize: z.number().min(12, "Font size must be at least 12").max(120, "Font size must be at most 120").default(48),
  strokeWidth: z
    .number()
    .min(0, "Stroke width must be at least 0")
    .max(20, "Stroke width must be at most 20")
    .default(4),
  convertTo: z.string().nullable().default(null),
  explicitLanguages: z.array(z.string()).default([]),
})

export type CaptionOptions = z.infer<typeof captionOptionsSchema>

export function validateCaptionOptions(options: unknown) {
  return captionOptionsSchema.safeParse(options)
}
