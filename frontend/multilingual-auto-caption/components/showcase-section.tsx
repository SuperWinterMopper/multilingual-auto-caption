import { ArrowRight } from "lucide-react"

export function ShowcaseSection() {
  const topShowcases = [
    {
      title: "Multi-language Detection",
      description: "Automatically detects and transcribes multiple languages in a single video",
      beforeImage: "/me-norm.png",
      afterImage1: "/me-eng.png",
      afterImage2: "/me-jap.png",
    },
    {
      title: "Language Conversion",
      description: "Convert to specific language you choose",
      beforeImage: "/ja.png",
      afterImage1: "/ja2en.png",
      afterImage2: "/ja2es.png",
    },
  ]

  const bottomShowcases = [
    {
      title: "Custom Styling",
      description: "Customize font size, colors, and stroke",
      leftImage: "/ko-white.png",
      rightImage: "/ko-red-chinese.png",
    },
    {
      title: "More Examples",
      description: "More examples",
      leftImage: "/es.png",
      rightImage: "/arab.png",
    },
  ]

  return (
    <section className="py-16">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-foreground mb-4">See MAC in action</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Real usage examples
        </p>
      </div>

      <div className="grid gap-10 md:grid-cols-2">
        {/* Top Row - Single image to two vertical images */}
        {topShowcases.map((showcase, index) => (
          <div key={index} className="space-y-4">
            <div className="flex items-center gap-4">
              {/* Single image on left */}
              <div className="flex-1 relative rounded-lg overflow-hidden border border-border">
                <img
                  src={showcase.beforeImage}
                  alt={`Before ${showcase.title}`}
                  className="w-full h-auto"
                />
                <span className="absolute top-2 left-2 bg-secondary/90 text-secondary-foreground text-xs px-2 py-1 rounded">
                  Before
                </span>
              </div>
              <ArrowRight className="h-6 w-6 text-primary shrink-0" />
              {/* Two images stacked vertically on right */}
              <div className="flex-1 flex flex-col gap-2">
                <div className="relative rounded-lg overflow-hidden border border-primary/50">
                  <img
                    src={showcase.afterImage1}
                    alt={`After ${showcase.title} 1`}
                    className="w-full h-auto"
                  />
                  <span className="absolute top-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                    After
                  </span>
                </div>
                <div className="relative rounded-lg overflow-hidden border border-primary/50">
                  <img
                    src={showcase.afterImage2}
                    alt={`After ${showcase.title} 2`}
                    className="w-full h-auto"
                  />
                  <span className="absolute top-2 left-2 bg-primary text-primary-foreground text-xs px-2 py-1 rounded">
                    After
                  </span>
                </div>
              </div>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-foreground">{showcase.title}</h3>
              <p className="text-sm text-muted-foreground">{showcase.description}</p>
            </div>
          </div>
        ))}

        {/* Bottom Row - Two horizontal images */}
        {bottomShowcases.map((showcase, index) => (
          <div key={index} className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex-1 relative rounded-lg overflow-hidden border border-border">
                <img
                  src={showcase.leftImage}
                  alt={`${showcase.title} example 1`}
                  className="w-full h-auto"
                />
              </div>
              <div className="flex-1 relative rounded-lg overflow-hidden border border-border">
                <img
                  src={showcase.rightImage}
                  alt={`${showcase.title} example 2`}
                  className="w-full h-auto"
                />
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
