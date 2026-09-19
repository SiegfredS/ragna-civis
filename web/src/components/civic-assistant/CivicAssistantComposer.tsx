import { useFormContext } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

import { useCivicAssistant } from "./hooks/useCivicAssistant";
import type { CivicAssistantFormValues } from "./types";

const helperTextId = "civic-assistant-composer-help";

export function CivicAssistantComposer() {
  const { handleSubmit, register, resetField, watch } =
    useFormContext<CivicAssistantFormValues>();
  const { isSubmitting, submitMessage } = useCivicAssistant();
  const message = watch("message");

  function onSubmit(values: CivicAssistantFormValues) {
    if (submitMessage(values.message)) {
      resetField("message");
    }
  }

  return (
    <form className="space-y-2 p-4" onSubmit={handleSubmit(onSubmit)}>
      <label className="text-sm font-medium" htmlFor="civic-assistant-message">
        Your question
      </label>
      <Textarea
        {...register("message")}
        id="civic-assistant-message"
        placeholder="Ask about an organization..."
        aria-describedby={helperTextId}
        maxLength={4000}
        rows={4}
      />
      <p id={helperTextId} className="text-xs text-muted-foreground">
        Each question is answered independently. Earlier messages are not used
        as context yet.
      </p>
      <div className="flex justify-end">
        <Button type="submit" disabled={isSubmitting || !message?.trim()}>
          Send
        </Button>
      </div>
    </form>
  );
}
