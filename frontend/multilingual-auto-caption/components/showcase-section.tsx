import { ArrowRight } from "lucide-react"

export function ShowcaseSection() {
  const showcases = [
    {
      before: "/video-frame-without-captions-dark-theme.jpg",
      after: "/video-frame-with-orange-multilingual-captions-over.jpg",
      title: "Multi-language Detection",
      description: "Automatically detects and transcribes multiple languages in a single video",
    },
    {
      before: "/hi_norm.png",
      after: "/hi_custom.png",
      title: "Custom Styling",
      description: "Customize font size, colors, and stroke to match your brand",
    },
    // {
    //   before: "/presentation-video-frame-without-text-overlay.jpg",
    //   after: "/presentation-video-frame-with-translated-captions.jpg",
    //   title: "Real-time Translation",
    //   description: "Translate captions to 30+ languages with a single click",
    // },
  ]

  return (
    <section className="py-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-foreground mb-4">See MAC in action</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Real examples
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {showcases.map((showcase, index) => (
          <div key={index} className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1 relative rounded-lg overflow-hidden border border-border">
                <img
                  src={showcase.before || "/placeholder.svg"}
                  alt={`Before ${showcase.title}`}
                  className="w-full h-auto"
                />
                <span className="absolute top-2 left-2 bg-secondary/90 text-secondary-foreground text-xs px-2 py-1 rounded">
                  Before
                </span>
              </div>
              <ArrowRight className="h-6 w-6 text-primary shrink-0" />
              <div className="flex-1 relative rounded-lg overflow-hidden border border-primary/50">
                <img
                  src={showcase.after || "/placeholder.svg"}
                  alt={`After ${showcase.title}`}
                  className="w-full h-auto"
                />
                <span className="absolute top-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                  After
                </span>
              </div>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-foreground">{showcase.title}</h3>
              <p className="text-sm text-muted-foreground">{showcase.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
