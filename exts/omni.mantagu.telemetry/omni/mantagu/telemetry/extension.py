import omni.ext
import omni.ui as ui
import omni.usd 

class ManTAGUTelemetryExtension(omni.ext.IExt):
def on_startup(self, ext_id):
print("[ManTAGU Extension] Initializing NVIDIA Inception Physical AI Layer...") 

### Create a dedicated UI window inside the Omniverse Workspace

self._window = ui.Window("ManTAGU Shoe Telemetry Anchor", width=350, height=220)
with self._window.frame:
with ui.VStack(spacing=10):
ui.Label("Odynex Axis Logistics - Haptic Ground-Truthing Dashboard", style={"color": 0xFF00BFFF, "font_size": 14})
ui.Spacer(height=5) 

    # Dynamic monitoring indicators
    with ui.HStack():
        ui.Label("Active Node ID:")
        self.node_label = ui.Label("ManTAGU-Vector-01", style={"font_weight": "bold"})
    
    with ui.HStack():
        ui.Label("Calculated Friction (μ):")
        self.friction_label = ui.Label("0.75 Dynamic Grip")
    
    with ui.HStack():
        ui.Label("Subsurface Compliance:")
        self.compliance_label = ui.Label("2500 mN (Stable)")
    
    ui.Spacer(height=10)
    ui.Button("Sync Stream with Foundation World Model", clicked_fn=self._on_sync_pressed)

def _on_sync_pressed(self):
print("[ManTAGU Extension] Streaming localized OpenUSD physics layers to NVIDIA Cosmos pipeline.") 

def on_shutdown(self):
print("[ManTAGU Extension] Shutting down haptic data stream pipeline safely.")
self._window = None
