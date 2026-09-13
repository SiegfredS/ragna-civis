import {
  CIVIC_ASSISTANT_ROLE,
  CIVIC_ASSISTANT_SESSION_STATUS,
} from "./constants";

export type CivicAssistantRole =
  (typeof CIVIC_ASSISTANT_ROLE)[keyof typeof CIVIC_ASSISTANT_ROLE];

export type CivicAssistantMessage = {
  id: string;
  role: CivicAssistantRole;
  text: string;
};

export type CivicAssistantFormValues = {
  message: string;
};

export type CivicAssistantSession =
  | {
      status: typeof CIVIC_ASSISTANT_SESSION_STATUS.CHECKING;
    }
  | {
      status: typeof CIVIC_ASSISTANT_SESSION_STATUS.SIGNED_OUT;
    }
  | {
      status: typeof CIVIC_ASSISTANT_SESSION_STATUS.AUTHENTICATED;
      userId: number;
    };
