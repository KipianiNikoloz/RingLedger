import { useMemo } from "react";

interface JsonBlockProps {
  title: string;
  data: unknown;
}

export function JsonBlock({ title, data }: JsonBlockProps): JSX.Element {
  const pretty = useMemo(() => JSON.stringify(data, null, 2), [data]);

  return (
    <section className="json-block">
      <h4>{title}</h4>
      <pre>{pretty}</pre>
    </section>
  );
}
