import sys

filepath = r'c:\Users\sshiv\youth_finance_bot\templates\index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS
css_addition = """
        @media (max-width: 768px) {
          #sidebar {
            position: fixed;
            top: 0; left: 0;
            height: 100vh;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
            z-index: 999;
          }
          #sidebar.open {
            transform: translateX(0);
          }
          #sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.5);
            z-index: 998;
          }
          #sidebar-overlay.open {
            display: block;
          }
          #main-content {
            margin-left: 0 !important;
          }
          #hamburger { display: block !important; }
        }
"""
content = content.replace("    </style>\n</head>", css_addition + "    </style>\n</head>")

# 2. Overlay
content = content.replace(
    '<body class="text-slate-100 h-screen overflow-hidden flex flex-col md:flex-row relative">',
    '<body class="text-slate-100 h-screen overflow-hidden flex flex-col md:flex-row relative">\n<div id="sidebar-overlay" onclick="closeSidebar()"></div>'
)

# 3. Sidebar ID and remove hidden md:flex
content = content.replace(
    '<aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 hidden md:flex z-15 shadow-xl">',
    '<aside id="sidebar" class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 z-15 shadow-xl">'
)

# 4. Language in sidebar
lang_html = """
                <div style="padding: 16px; border-top: 1px solid #334155; margin-top: 16px;">
                  <p style="color:#64748b; font-size:11px; margin-bottom:8px;">
                    LANGUAGE
                  </p>
                  <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <button onclick="setLang('english')" 
                      style="background:#1e293b; color:#94a3b8; border:1px solid #334155; 
                      padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;">
                      EN
                    </button>
                    <button onclick="setLang('hindi')" 
                      style="background:#1e293b; color:#94a3b8; border:1px solid #334155; 
                      padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;">
                      हिंदी
                    </button>
                    <button onclick="setLang('telugu')" 
                      style="background:#1e293b; color:#94a3b8; border:1px solid #334155; 
                      padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;">
                      తెలుగు
                    </button>
                    <button onclick="setLang('tamil')" 
                      style="background:#1e293b; color:#94a3b8; border:1px solid #334155; 
                      padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;">
                      தமிழ்
                    </button>
                  </div>
                </div>
            </nav>
        </div>"""
import re
content = re.sub(r'</nav>\s*</div>\s*<!-- Sidebar Footer Removed -->\s*</aside>', lang_html + '\n        <!-- Sidebar Footer Removed -->\n    </aside>', content)

# 5. Remove Mobile Navbar and Drawer
content = re.sub(r'<!-- Top Mobile Navbar -->.*?<!-- Main Content Container -->', '<!-- Main Content Container -->', content, flags=re.DOTALL)

# 6. main-content ID
content = content.replace(
    '<main class="flex-1 flex flex-col overflow-hidden bg-slate-950 relative h-full">',
    '<main id="main-content" class="flex-1 flex flex-col overflow-hidden bg-slate-950 relative h-full">'
)

# 7. Header Replacement
new_header = """        <header class="bg-slate-900/60 border-b border-slate-800/80 p-4 flex justify-between items-center z-10 shrink-0 shadow-md">
            <div class="flex items-center gap-3 w-1/3">
                <button id="hamburger" onclick="toggleSidebar()" 
                  style="background:transparent; border:none; color:white; 
                  font-size:22px; cursor:pointer; padding:4px 8px;
                  display:none;">
                  ☰
                </button>
                <div class="flex items-center gap-2">
                    <i class="fas fa-shield-halved text-blue-500 text-2xl hidden md:block"></i>
                    <h1 class="heading-font font-bold text-lg text-white hidden md:block">YFG Guardian</h1>
                </div>
            </div>
            
            <div class="w-1/3 text-center flex justify-center">
                <h1 class="heading-font text-lg font-bold text-white flex items-center justify-center gap-2">
                    <span id="active-tab-title">Financial Health Dashboard</span>
                </h1>
            </div>
            
            <div class="flex items-center gap-3 w-1/3 justify-end">
                <div id="auth-section" style="display:flex; align-items:center; gap:12px;">
                  <div id="guest-ui">
                    <button onclick="signInWithGoogle()" 
                      style="background:#4285F4; color:white; border:none; 
                      padding:8px 16px; border-radius:6px; cursor:pointer; 
                      font-size:13px; display:flex; align-items:center; gap:8px;">
                      <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" 
                        width="16" height="16"/>
                      <span class="hidden sm:inline">Sign in with Google</span>
                    </button>
                  </div>
                  <div id="google-ui" style="display:none; align-items:center; gap:10px;">
                    <img id="user-photo" src="" width="32" height="32" 
                      style="border-radius:50%; border:2px solid #4285F4;"/>
                    <button onclick="signOut()" 
                      style="background:transparent; color:#94a3b8; border:1px solid #334155; 
                      padding:4px 10px; border-radius:4px; cursor:pointer; font-size:12px;">
                      Sign Out
                    </button>
                  </div>
                </div>
            </div>
        </header>"""
content = re.sub(r'<!-- Top Toolbar Header -->.*?</header>', '<!-- Top Toolbar Header -->\n' + new_header, content, flags=re.DOTALL)

# 8. View Container padding
content = content.replace(
    '<div id="view-container" class="flex-1 overflow-y-auto p-4 md:p-6 w-full relative">',
    '<div id="view-container" class="flex-1 overflow-y-auto p-4 md:p-6 w-full relative" style="padding-bottom: 80px;">'
)

# 9. Bottom Action Bar and JS
bottom_bar = """<div id="bottom-action-bar" style="
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #1e293b;
  border-top: 1px solid #334155;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  z-index: 1000;
">
  <button onclick="executeSaveProfile()" style="
    flex: 1;
    background: #3b82f6;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  ">💾 Save Profile</button>

  <button onclick="downloadReport()" style="
    flex: 1;
    background: #10b981;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  ">📄 Report</button>
</div>
<script>
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}
</script>"""
content = content.replace('</body>\n</html>', bottom_bar + '\n</body>\n</html>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('UI fixes applied successfully.')
