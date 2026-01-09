export default function Header() {
    return (
        <div className="text-center flex flex-col justify-center mb-12 h-50">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-4 text-balance font-(family-name:--font-caveat)">
            Multilingual Auto Caption
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto text-pretty">
            Caption your multilingual videos automatically, whatever the languages
          </p>
        </div>
    )
}