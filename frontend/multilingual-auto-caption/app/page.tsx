import { VideoUploader } from "@/components/video-uploader"
import { ShowcaseSection } from "@/components/showcase-section"
import { Footer } from "@/components/footer"
import Header from "@/components/header"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 container mx-auto px-4 py-12">
        <Header />
        <VideoUploader />
        <ShowcaseSection />
      </main>
      <Footer />
    </div>
  )
}
