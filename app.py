import streamlit as st
import pandas as pd
import time
import os
import sys
import asyncio
from maps_scraper import scrape_google_maps
from website_analyzer import analyze_website_quality
from email_extractor import extract_emails_from_site
from csv_manager import save_to_new_csv, get_all_runs, update_csv_field
from email_generator import generate_ai_email
from email_sender import send_outreach_email

from dotenv import load_dotenv

load_dotenv()

# --- Playwright Cloud Setup ---
def install_playwright_browsers():
    try:
        import subprocess
        import sys
        # Check if chromium is installed
        result = subprocess.run([sys.executable, "-m", "playwright", "inspect"], capture_output=True, text=True)
        # If it fails or executable is missing, install it
        # We also check for 'chromium' in the env to be sure
        log_dir = os.path.expanduser("~/.cache/ms-playwright")
        if not os.path.exists(log_dir) or "chromium" not in str(result.stderr).lower():
            st.info("Preparing environment (First time setup)...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            st.success("Environment Ready!")
    except Exception as e:
        st.warning(f"Note: Playwright auto-install attempt failed: {e}. If search crashes, run 'playwright install' manually.")

# Windows Policy Fix for Playwright
if sys.platform == 'win32':
    try:
        import asyncio
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass
else:
    # On Linux/Cloud, try to install browsers at startup
    install_playwright_browsers()

# --- Page Config ---
st.set_page_config(page_title="LeadFlow AI Pro V3", layout="wide", page_icon="🚀")

# --- AUTHENTICATION ---
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔐 Agent Login")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            # Get password from .env
            admin_pass = os.getenv("ADMIN_PASSWORD", "hussain123")
            if password == admin_pass:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect Password. Please check your .env file.")
        return False
    return True

if check_auth():
    st.sidebar.title("🤖 AI Lead Agent")
    st.sidebar.info(f"Logged in as: Hussain")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.rerun()
        
    page = st.sidebar.radio("Navigate", ["Lead Discovery", "Results History", "Email Center"])
else:
    st.stop()

# --- Lead Discovery Page ---
if page == "Lead Discovery":
    st.title("🔎 Premium Lead Discovery")
    st.write("Targeting Google Maps for high-value prospects.")
    
    col1, col2 = st.columns(2)
    with col1:
        industry = st.text_input("Industry", placeholder="e.g. plumber")
    with col2:
        location = st.text_input("City/Country", placeholder="e.g. London")
    
    target_valid = st.number_input("Target Number of Valid Leads (Weak Webs + Emails)", min_value=1, max_value=200, value=20)
    
    if st.button("🚀 Start Harvesting"):
        if not industry or not location:
            st.warning("Please enter both industry and location.")
        else:
            with st.status("🔍 Agent Activity Log", expanded=True) as status:
                log_box = st.empty()
                logs = []

                def update_logs(msg):
                    logs.append(f"• {msg}")
                    # Join with double newlines and add a trailing newline for clear separation
                    log_box.markdown("\n\n".join(logs[-12:]) + "\n\n---")

                update_logs("Lead Agent activated...")
                final_leads = []
                fully_processed_names = set() # Avoid duplicates across ALL attempts
                
                valid_count_text = st.empty()
                
                # Keywords to vary the search if we don't find enough
                search_variants = [
                    f"{industry}",
                    f"top {industry}",
                    f"best {industry}",
                    f"{industry} services",
                    f"local {industry}"
                ]
                
                variant_idx = 0
                while len(final_leads) < target_valid and variant_idx < len(search_variants):
                    current_query = search_variants[variant_idx]
                    update_logs(f"Attempting batch {variant_idx + 1} with query: '{current_query}' in {location}")
                    
                    # Fetch a batch (e.g., 50 at a time)
                    raw_leads = scrape_google_maps(current_query, location, max_results=60, update_func=update_logs)
                    
                    if not raw_leads:
                        update_logs("No more results for this variant. Switching to next...")
                        variant_idx += 1
                        continue

                    update_logs(f"Auditing results for batch {variant_idx + 1}...")
                    
                    for lead in raw_leads:
                        if len(final_leads) >= target_valid:
                            break
                            
                        name = lead['company_name']
                        if name in fully_processed_names:
                            continue
                        fully_processed_names.add(name)
                        
                        url = lead['website_url']
                        update_logs(f"Checking: {name}")
                        
                        # Analyze website
                        status_val, problem = analyze_website_quality(url)
                        
                        # Only process if we have a valid-looking email
                        email = extract_emails_from_site(url)
                        
                        # VALIDATION: email must be a non-empty string and not just junk
                        is_valid_email = email and len(email.strip()) > 3 and "@" in email

                        if (status_val in ["NO_WEBSITE", "WEAK_WEBSITE"]) and is_valid_email:
                            lead.update({
                                "email": email,
                                "website_status": status_val,
                                "problem_detected": problem,
                                "email_sent": "NO"
                            })
                            final_leads.append(lead)
                            valid_count_text.info(f"✅ Found Valid Lead: {name} ({len(final_leads)}/{target_valid})")
                        elif not is_valid_email and (status_val in ["NO_WEBSITE", "WEAK_WEBSITE"]):
                            update_logs(f"Skipping {name}: No valid email found on site.")
                    
                    variant_idx += 1
                    if variant_idx >= len(search_variants) and len(final_leads) < target_valid:
                        update_logs("All search variants exhausted. Closing search.")
                        break
                        
                    if len(final_leads) < target_valid:
                        update_logs(f"Quota not met ({len(final_leads)}/{target_valid}). Trying another search variant...")
                        time.sleep(2) # Avoid aggressive retries

                update_logs("Discovery process finalized.")
                time.sleep(1) # Small pause for UI stability

                if final_leads:
                    filepath = save_to_new_csv(final_leads)
                    st.success(f"Task Perfected! Collected {len(final_leads)} verified prospects.")
                    st.dataframe(pd.DataFrame(final_leads), width="stretch")
                else:
                    st.error("No prospects found matching your criteria even after multiple attempts.")
                
                status.update(label="Discovery & Audit Finished!", state="complete")

# --- Results History Page ---
elif page == "Results History":
    st.title("📂 Discovery History")
    
    runs = get_all_runs()
    if not runs:
        st.info("No runs found yet.")
    else:
        for run_path in runs:
            filename = os.path.basename(run_path)
            st.subheader(f"📊 {filename}")
            df = pd.read_csv(run_path)
            st.dataframe(df, width="stretch")
            st.markdown("---")

# --- Email Center Page ---
elif page == "Email Center":
    st.title("📧 Outreach Command Center")
    
    runs = get_all_runs()
    if not runs:
        st.info("No leads available.")
    else:
        selected_run = st.selectbox("Select Discovery Run", runs, format_func=lambda x: os.path.basename(x))
        df = pd.read_csv(selected_run)
        
        # Filter for leads with emails (already should be filtered but just in case)
        leads_with_email = df[df['email'].notna()]
        
        if leads_with_email.empty:
            st.warning("No leads in this run have extracted emails.")
        else:
            st.write("### Review & Select Prospects")
            st.write("Mark the checkbox for leads you want to contact. Review the detected problems in the table below.")
            
            # Interactive Table
            edit_df = leads_with_email.copy()
            edit_df.insert(0, "Select", False)
            
            selected_df = st.data_editor(
                edit_df[["Select", "company_name", "email", "problem_detected", "email_sent"]],
                key="email_editor",
                width="stretch",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", default=False),
                    "company_name": st.column_config.TextColumn("Company Name", width="medium"),
                    "email": st.column_config.TextColumn("Email", width="medium"),
                    "problem_detected": st.column_config.TextColumn("Website Problem", width="large"),
                    "email_sent": st.column_config.TextColumn("Sent?", width="small")
                },
                disabled=["company_name", "email", "problem_detected", "email_sent"]
            )
            
            selected_rows = selected_df[selected_df["Select"] == True]
            
            col_a, col_b = st.columns(2)
            with col_a:
                gen_btn = st.button("🪄 Generate AI Pitches")
            with col_b:
                send_btn = st.button("🚀 Dispatch Batch")

            if gen_btn:
                if selected_rows.empty:
                    st.error("Please select at least one prospect.")
                else:
                    for idx, row in selected_rows.iterrows():
                        with st.spinner(f"AI is drafting email for {row['company_name']}..."):
                            email_body = generate_ai_email(row['company_name'], row['website_status'], row['problem_detected'])
                            st.session_state[f"draft_{row['company_name']}"] = email_body
                            st.markdown(f"#### Pitch: {row['company_name']}")
                            st.text_area("Draft Content", email_body, height=200, key=f"area_{row['company_name']}")

            if send_btn:
                if selected_rows.empty:
                    st.error("Select leads first.")
                else:
                    sent_count = 0
                    for idx, row in selected_rows.iterrows():
                        draft_key = f"draft_{row['company_name']}"
                        if draft_key in st.session_state:
                            draft = st.session_state[draft_key]
                            subject = f"Improving your business online: {row['company_name']}"
                            
                            primary_email = row['email'].split(',')[0].strip()
                            success = send_outreach_email(primary_email, subject, draft)
                            
                            if success:
                                sent_count += 1
                                update_csv_field(selected_run, row['company_name'], 'email_sent', 'YES')
                                st.toast(f"✅ Sent to {row['company_name']}")
                            else:
                                st.error(f"❌ Failed to reach {row['company_name']}")
                        else:
                            st.warning(f"No draft found for {row['company_name']}. Generate pitch first.")
                    
                    if sent_count > 0:
                        st.success(f"Batch completed! {sent_count} emails successfully dispatched.")
                        st.rerun()
