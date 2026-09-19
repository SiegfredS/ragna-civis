import { Link } from "@tanstack/react-router";

import { buttonVariants } from "@/components/ui/button";
import {
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

import { CivicAssistantChat } from "./CivicAssistantChat";

export function CivicAssistantPanel() {
  return (
    <SheetContent
      side="right"
      className="inset-auto! right-4! bottom-4! h-[min(42rem,calc(100dvh-2rem))]! w-[calc(100vw-2rem)]! max-w-sm! gap-0! rounded-lg border! p-0!"
    >
      <SheetHeader className="border-b pr-12">
        <SheetTitle>Civic Assistant</SheetTitle>
        <SheetDescription>
          Get quick answers about Ragna Civis organizations.
        </SheetDescription>
      </SheetHeader>
      <CivicAssistantChat mode="compact" />
      <SheetFooter className="border-t">
        <Link
          to="/assistant"
          className={buttonVariants({ variant: "outline" })}
        >
          Open full chat
        </Link>
      </SheetFooter>
    </SheetContent>
  );
}
