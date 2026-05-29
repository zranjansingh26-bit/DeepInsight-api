"use client";

import { Container } from "@/components/ui/container";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { faqs } from "@/lib/site";

export function FAQ() {
  return (
    <section id="faq" className="section bg-cloud/60">
      <Container className="max-w-3xl">
        <div className="text-center">
          <span className="eyebrow">FAQ</span>
          <h2 className="mt-5 section-title text-balance">
            Questions,{" "}
            <span className="gradient-text">answered honestly.</span>
          </h2>
          <p className="mt-5 lead">
            Still unsure?{" "}
            <a
              href="#"
              className="font-semibold text-violet-700 hover:text-violet-800"
            >
              Email the team →
            </a>
          </p>
        </div>

        <Accordion type="single" collapsible className="mt-12 space-y-3">
          {faqs.map((f, i) => (
            <AccordionItem key={f.q} value={`item-${i}`}>
              <AccordionTrigger>{f.q}</AccordionTrigger>
              <AccordionContent>{f.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </Container>
    </section>
  );
}
