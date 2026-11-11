import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft, HelpCircle, MessageSquare, FileQuestion, Mail, Send, CheckCircle } from "lucide-react";
import { Link } from "wouter";
import { Sidebar, Topbar } from "@/components/Navigation";
import { useToast } from "@/hooks/use-toast";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const FAQ_ITEMS = [
  {
    question: "How do I create a post?",
    answer: "Click the 'Create Post' button on the home page. You can share text, images, or PDFs. Choose the category that best fits your content."
  },
  {
    question: "What are anonymous confessions?",
    answer: "Confessions are posts where your identity is hidden from other users. Only admins can see who posted. Use this for sharing thoughts you'd prefer to keep private."
  },
  {
    question: "How do I share study notes?",
    answer: "Select 'Notes' as the category when creating a post. You can upload PDFs or images of your notes to share with classmates."
  },
  {
    question: "Can I follow other users?",
    answer: "Yes! Visit a user's profile and click the 'Follow' button. You'll see their posts in your feed."
  },
  {
    question: "How do I report inappropriate content?",
    answer: "Click the three dots menu on any post and select 'Report'. Describe the issue and our admin team will review it."
  },
  {
    question: "Why was my account suspended?",
    answer: "Accounts may be suspended for violating community guidelines. Check your messages for admin warnings. Contact support if you believe this was a mistake."
  },
  {
    question: "How do I change my profile emoji?",
    answer: "Go to Settings and click on your current emoji to change it. Choose from hundreds of emojis to represent yourself!"
  },
  {
    question: "How does the community chat work?",
    answer: "The community chat is a group space where all users can send messages visible to everyone. It's great for quick discussions and announcements."
  }
];

export default function HelpPage() {
  const { toast } = useToast();
  const [contactForm, setContactForm] = useState({ subject: "", message: "" });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    if (!contactForm.subject || !contactForm.message) return;
    setSubmitted(true);
    toast({ title: "Message sent!", description: "We'll get back to you soon." });
    setContactForm({ subject: "", message: "" });
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Topbar />
      <Sidebar />

      <main className="pt-24 lg:pl-72 pb-12 px-4 max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
          <Link href="/">
            <Button variant="ghost" size="icon" data-testid="button-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold">Help & Support</h1>
            <p className="text-muted-foreground text-sm">Find answers or contact us</p>
          </div>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileQuestion className="w-5 h-5" />
                Frequently Asked Questions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Accordion type="single" collapsible className="w-full">
                {FAQ_ITEMS.map((item, i) => (
                  <AccordionItem key={i} value={`item-${i}`}>
                    <AccordionTrigger className="text-left">
                      {item.question}
                    </AccordionTrigger>
                    <AccordionContent className="text-muted-foreground">
                      {item.answer}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="w-5 h-5" />
                Contact Support
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {submitted ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                  <p className="font-medium">Thanks for reaching out!</p>
                  <p className="text-sm text-muted-foreground">We'll respond as soon as possible.</p>
                </div>
              ) : (
                <>
                  <Input
                    placeholder="Subject"
                    value={contactForm.subject}
                    onChange={(e) => setContactForm({ ...contactForm, subject: e.target.value })}
                    data-testid="input-help-subject"
                  />
                  <Textarea
                    placeholder="Describe your issue or question..."
                    rows={5}
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    data-testid="input-help-message"
                  />
                  <Button 
                    onClick={handleSubmit} 
                    disabled={!contactForm.subject || !contactForm.message}
                    className="w-full gap-2"
                    data-testid="button-send-help"
                  >
                    <Send className="w-4 h-4" />
                    Send Message
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5" />
                Quick Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Use the search bar to find posts, notes, or people
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Click on any user's profile to follow them or send a message
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Report any content that violates community guidelines
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  Customize your theme in Settings for a personalized experience
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
