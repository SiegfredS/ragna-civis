import { z } from "zod";

const civicAssistantDeltaEventSchema = z
  .object({
    type: z.literal("delta"),
    text: z.string().min(1),
  })
  .strict();

const civicAssistantDoneEventSchema = z
  .object({
    type: z.literal("done"),
  })
  .strict();

const civicAssistantErrorEventSchema = z
  .object({
    type: z.literal("error"),
    code: z.literal("assistant_unavailable"),
    message: z.literal("The assistant could not finish. Please try again."),
  })
  .strict();

export const civicAssistantStreamEventSchema = z.discriminatedUnion("type", [
  civicAssistantDeltaEventSchema,
  civicAssistantDoneEventSchema,
  civicAssistantErrorEventSchema,
]);

export type CivicAssistantStreamEvent = z.infer<
  typeof civicAssistantStreamEventSchema
>;
