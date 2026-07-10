---
name: Orbit Beraterprofil
description: Modern Streamlit UI for ORBIT consultant profile generation
colors:
  primary: "#0F172A"
  secondary: "#64748B"
  tertiary: "#0891B2"
  accent: "#06B6D4"
  neutral: "#F1F5F9"
  surface: "#FFFFFF"
  on-primary: "#FFFFFF"
  on-tertiary: "#FFFFFF"
  border: "#D8E3EA"
  success: "#059669"
  warning: "#D97706"
  error: "#DC2626"
typography:
  display:
    fontFamily: "DM Sans, Segoe UI, sans-serif"
    fontSize: 2.25rem
    fontWeight: 700
  h2:
    fontFamily: "DM Sans, Segoe UI, sans-serif"
    fontSize: 1.25rem
    fontWeight: 600
  body:
    fontFamily: "DM Sans, Segoe UI, sans-serif"
    fontSize: 1rem
    fontWeight: 400
  label-caps:
    fontFamily: "DM Sans, Segoe UI, sans-serif"
    fontSize: 0.75rem
    fontWeight: 600
    letterSpacing: 0.08em
rounded:
  sm: 8px
  md: 14px
  lg: 20px
spacing:
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-tertiary}"
    rounded: "{rounded.md}"
    padding: 12px
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: 24px
  badge-success:
    backgroundColor: "{colors.success}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
---

## Overview

Professional, calm interface for HR and consultants. Evokes ORBIT's telecom consulting brand: deep navy structure, teal accents, generous whitespace. Avoid generic purple gradients and cluttered dashboards.

## Colors

- **Primary (#0B1F2A):** Headers, sidebar, hero text.
- **Secondary (#5B7A8C):** Metadata, captions, borders.
- **Tertiary (#0D9488):** Primary actions, active states, key highlights.
- **Accent (#14B8A6):** Subtle gradients and hover glow.
- **Neutral (#F4F7F9):** Page background — warmer than pure white.

## Typography

DM Sans for a modern, readable SaaS feel. Section labels use small caps styling.

## Layout

Wide layout with left sidebar for inputs and main area for preview. Cards with soft shadows group upload, options, and results.

## Components

- Upload zone with dashed border and teal hover.
- Status badges for LLM online/offline.
- Three-column profile preview mirroring the PowerPoint slide.

## Do's and Don'ts

- Do keep German UI copy for consultant-facing labels.
- Do show audit warnings prominently before export.
- Don't invent CV facts — surface LLM warnings instead.
- Don't use more than one accent color family.
