import Layout from "../components/Layout";
import ChatInterface from "../components/ChatInterface";

export default function ChatPage({ token, setToken }) {
  return (
    <Layout token={token} setToken={setToken}>
      <ChatInterface token={token} />
    </Layout>
  );
}
