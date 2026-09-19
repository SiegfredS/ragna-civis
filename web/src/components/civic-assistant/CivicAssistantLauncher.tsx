import { useState } from "react";

import { MessageCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet } from "@/components/ui/sheet";

import { CivicAssistantPanel } from "./CivicAssistantPanel";

export function CivicAssistantLauncher() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <Button
        type="button"
        className="fixed right-4 bottom-4 z-40 rounded-full shadow-lg"
        size="icon-lg"
        aria-label="Open Civic Assistant"
        onClick={() => setIsOpen(true)}
      >
        <MessageCircle />
      </Button>
      <CivicAssistantPanel />
    </Sheet>
  );
}
