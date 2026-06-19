import { useState } from "react";

import { Assent } from "./pages/Assent";
import { Chat } from "./pages/Chat";
import { Feedback } from "./pages/Feedback";
import { GameSelection } from "./pages/GameSelection";
import { Welcome } from "./pages/Welcome";
import type { Conversation, Game, LearningSession, Student } from "./types/api";

type Screen = "welcome" | "assent" | "selection" | "chat" | "feedback";

export default function App() {
  const [screen, setScreen] = useState<Screen>("welcome");
  const [student, setStudent] = useState<Student | null>(null);
  const [session, setSession] = useState<LearningSession | null>(null);
  const [currentGame, setCurrentGame] = useState<Game | null>(null);
  const [conversation, setConversation] = useState<Conversation | null>(null);

  const reset = () => {
    setScreen("welcome");
    setStudent(null);
    setSession(null);
    setCurrentGame(null);
    setConversation(null);
  };

  if (screen === "welcome") {
    return (
      <Welcome
        onValidated={(validatedStudent) => {
          setStudent(validatedStudent);
          setScreen("assent");
        }}
      />
    );
  }

  if (screen === "assent" && student) {
    return (
      <Assent
        student={student}
        onAccepted={(createdSession) => {
          setSession(createdSession);
          setScreen("selection");
        }}
        onRejected={reset}
      />
    );
  }

  if (screen === "selection" && student && session) {
    return (
      <GameSelection
        student={student}
        session={session}
        onSelected={(selectedGame, openedConversation) => {
          setCurrentGame(selectedGame);
          setConversation(openedConversation);
          setScreen("chat");
        }}
      />
    );
  }

  if (screen === "chat" && student && session && currentGame && conversation) {
    return (
      <Chat
        student={student}
        session={session}
        game={currentGame}
        conversation={conversation}
        onConversationUpdated={setConversation}
        onBack={() => setScreen("selection")}
        onFinished={(closedSession) => {
          setSession(closedSession);
          setScreen("feedback");
        }}
      />
    );
  }

  if (screen === "feedback" && student && session) {
    return <Feedback student={student} session={session} onDone={reset} />;
  }

  return (
    <Welcome
      onValidated={(validatedStudent) => {
        setStudent(validatedStudent);
        setScreen("assent");
      }}
    />
  );
}
