import { z } from "zod";

import { meSchema } from "./schemas";

export type Me = z.infer<typeof meSchema>;
