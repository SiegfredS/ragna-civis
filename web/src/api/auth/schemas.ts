import { z } from "zod";

export const meSchema = z.object({
  id: z.number(),
  username: z.string(),
  email: z.string().nullable(),
  firstName: z.string(),
  middleName: z.string(),
  lastName: z.string(),
  avatar: z.string().nullable(),
});

export const loginResponseSchema = z.object({
  token: z.string().min(1),
  expiry: z.string(),
  user: z.object({
    id: z.number(),
    username: z.string(),
    email: z.string().nullable(),
    firstName: z.string(),
    middleName: z.string(),
    lastName: z.string(),
  }),
});
