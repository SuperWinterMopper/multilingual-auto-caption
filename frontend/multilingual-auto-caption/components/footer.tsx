import { Github, Linkedin, Mail } from "lucide-react"

export function Footer() {
  const links = [
    {
      name: "GitHub",
      href: "https://github.com/SuperWinterMopper",
      icon: Github,
    },
    {
      name: "LinkedIn",
      href: "https://www.linkedin.com/in/keigo-healy",
      icon: Linkedin,
    },
    {
      name: "Email",
      href: "mailto:keigo@u.northwestern.edu",
      icon: Mail,
    },
  ]

  return (
    <footer className="border-t border-border py-8 mt-16">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            built by Keigo Healy
          </p>
          <div className="flex items-center gap-6">
            {links.map((link) => (
              <a
                key={link.name}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors flex items-center gap-2"
              >
                <link.icon className="h-5 w-5" />
                <span className="sr-only">{link.name}</span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
