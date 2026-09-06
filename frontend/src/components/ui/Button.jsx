// A button with real states: hover, a genuine pressed feel, focus for keyboard
// users, disabled, and a loading state that spins its own icon.

import Icon from "./Icon";

export default function Button({
  children,
  variant = "default",     // default | primary | ghost | danger | ok
  size = "md",             // md | sm
  icon,                    // an Icon name, drawn before the text
  loading = false,
  disabled = false,
  className = "",
  ...rest
}) {
  const classes = [
    "btn",
    variant !== "default" ? `btn-${variant}` : "",
    size === "sm" ? "btn-sm" : "",
    loading ? "is-loading" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={classes} disabled={disabled || loading} {...rest}>
      {loading ? (
        <Icon name="refresh" className="spin" size={size === "sm" ? 14 : 16} />
      ) : icon ? (
        <Icon name={icon} size={size === "sm" ? 14 : 16} />
      ) : null}
      {children && <span>{children}</span>}
    </button>
  );
}
