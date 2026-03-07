---
name: openclaw-nodes
description: Manage paired mobile/desktop nodes (Android, iOS, macOS) connected to the OpenClaw gateway. Use when: (1) checking paired device status, (2) taking photos with phone camera, (3) getting device location, (4) reading phone notifications, (5) recording screen on paired device, (6) sending notifications to paired device, (7) running commands on node host, (8) using canvas on mobile device, (9) user mentions "phone", "device", "camera", "location", "screenshot", "notification", "paired device", or "node".
---

# OpenClaw Nodes Skill

Nodes are companion devices (Android/iOS/macOS) connected to the gateway via WebSocket.

## Check Node Status

```bash
openclaw nodes status
openclaw nodes describe --node <id-or-name>
```

Or use the `nodes` tool directly:
- `nodes(action="status")` — list all paired nodes
- `nodes(action="describe", node="<name>")` — detailed info

## Device Pairing

New devices need approval:
```bash
openclaw devices list          # show pending + approved
openclaw devices approve <id>  # approve a pending device
openclaw devices reject <id>   # reject
```

Or use tool: `nodes(action="pending")`, `nodes(action="approve", requestId="<id>")`

## Camera (Photos + Video)

Take photo from paired phone:
- `nodes(action="camera_snap", node="<name>")` — both cameras
- `nodes(action="camera_snap", node="<name>", facing="front")` — selfie
- `nodes(action="camera_snap", node="<name>", facing="back")` — rear

List available cameras:
- `nodes(action="camera_list", node="<name>")`

Record video clip:
- `nodes(action="camera_clip", node="<name>", durationMs=10000)` — 10s clip
- `nodes(action="camera_clip", node="<name>", durationMs=5000, facing="front")`

⚠️ Device must be **foregrounded** for camera/screen operations.

## Location

Get device GPS location:
- `nodes(action="location_get", node="<name>")`
- `nodes(action="location_get", node="<name>", desiredAccuracy="precise")`

Returns: latitude, longitude, accuracy (meters), timestamp.
Location must be enabled in the device app settings.

## Notifications

Read device notifications:
- `nodes(action="notifications_list", node="<name>")`

Act on a notification:
- `nodes(action="notifications_action", node="<name>", notificationKey="<key>", notificationAction="open")`
- `nodes(action="notifications_action", node="<name>", notificationKey="<key>", notificationAction="dismiss")`
- `nodes(action="notifications_action", node="<name>", notificationKey="<key>", notificationAction="reply", notificationReplyText="Got it")`

## Screen Recording

Record device screen:
- `nodes(action="screen_record", node="<name>", durationMs=10000)` — 10s
- `nodes(action="screen_record", node="<name>", durationMs=10000, includeAudio=false)`

Max duration: 60 seconds. Device must be foregrounded.

## Send Notification to Device

Push a notification to the paired device:
- `nodes(action="notify", node="<name>", title="Alert", body="Task complete")`
- `nodes(action="notify", node="<name>", title="Urgent", body="Check this", priority="timeSensitive")`

## Run Commands on Node Host

Execute commands on the remote node:
- `nodes(action="run", node="<name>", command=["echo", "hello"])`
- `nodes(action="run", node="<name>", command=["uname", "-a"])`

Requires exec approvals on the node. Use allowlist mode for safety.

## Device Info

- `nodes(action="device_status", node="<name>")` — battery, network, storage
- `nodes(action="device_info", node="<name>")` — model, OS version
- `nodes(action="device_permissions", node="<name>")` — granted permissions
- `nodes(action="device_health", node="<name>")` — health metrics

## Canvas (Push UI to Device)

Present a URL on the device:
- `canvas(action="present", node="<name>", url="https://example.com")`

Push A2UI content:
- `canvas(action="a2ui_push", node="<name>", jsonl="...")`

Take a snapshot of what's on screen:
- `canvas(action="snapshot", node="<name>")`

## Constraints

- Camera/screen require device to be foregrounded
- Location requires user permission in app settings
- SMS requires Android with telephony + permission
- Video clips clamped to ≤60 seconds
- Node must be on same network or connected via tunnel
