// What a screen shows when there is nothing to show. A bare sentence in grey
// looks like a bug; this looks deliberate.

import Icon from "./Icon";

export default function EmptyState({ icon = "inbox", title, children, action }) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Icon name={icon} size={24} />
      </div>
      <p className="empty-title">{title}</p>
      {children && <p className="empty-text">{children}</p>}
      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}
