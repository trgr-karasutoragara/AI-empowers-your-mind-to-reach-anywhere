#!/usr/bin/env python3
"""
.txt/md Is All You Need - Simple Edition
Simplified for developing countries and easy setup
No local AI required - just internet connection

Designed for developing countries and anyone seeking a distraction-free reading experience. Works on any Ubuntu system - read books completely offline, with optional AI chat when internet is available. No complex setup required.

Usage:
    python3 just-zen.py

Environment Variables:
    GEMINI_API_KEY    - Required for AI features

Commands (when API available):
    ask <question>   - Ask AI about the text
    add <note>       - Add reading note
    find <text>      - Search in book
    goto <line>      - Jump to line number
    export           - Export notes and chat
    notes            - Show your notes
    history          - Show recent questions
    help, h          - Show help
    quit, q          - Exit

Navigation:
    - Enter: Next page
    - ↑ (Up arrow): Previous page
    - ↓ (Down arrow): Next page  
    - ← (Left arrow): Previous line
    - → (Right arrow): Next line
    - number + Enter: Jump to line
"""

import os
import sys
import glob
import json
import textwrap
import sqlite3
import termios
import tty
from datetime import datetime

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class SimpleReader:
    def __init__(self, book_path=None):
        # シンプルなAPI確認
        self.has_api = self.check_api()
        
        # If no book specified, show file browser
        if book_path is None:
            book_path = self.select_book_from_folder()
            if book_path is None:
                sys.exit(0)
        
        self.book_path = book_path
        self.book_name = os.path.basename(book_path)
        
        # Display settings
        self.lines_per_page = 20
        self.current_line = 0
        
        # Load book
        self.book_content = self.load_book()
        if not self.book_content:
            print(f"Error: Could not load {book_path}")
            sys.exit(1)
        
        self.book_lines = self.book_content.split('\n')
        
        # データベース初期化（APIがある場合のみ）
        if self.has_api:
            self.db_path = f"{self.book_name}_simple.db"
            self.init_database()
    
    def check_api(self):
        """シンプルなAPI確認"""
        if not GEMINI_AVAILABLE:
            return False
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return False
        
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
            return True
        except:
            return False
    
    def getch(self):
        """Get single character input including arrow keys"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if char == '\x1b':
                char += sys.stdin.read(2)
                
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    
    def get_input_with_navigation(self):
        """Get input that handles both commands and arrow key navigation"""
        print("\n> Press arrow keys for navigation, or type command: ", end='', flush=True)
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Set terminal to raw mode for immediate key detection
            tty.setraw(fd)
            
            input_buffer = ""
            
            while True:
                char = sys.stdin.read(1)
                
                # Handle escape sequences (arrow keys)
                if char == '\x1b':
                    seq = sys.stdin.read(2)
                    full_seq = char + seq
                    
                    if full_seq == '\x1b[A':  # Up arrow
                        return 'ARROW_UP'
                    elif full_seq == '\x1b[B':  # Down arrow
                        return 'ARROW_DOWN'
                    elif full_seq == '\x1b[C':  # Right arrow
                        return 'ARROW_RIGHT'
                    elif full_seq == '\x1b[D':  # Left arrow
                        return 'ARROW_LEFT'
                
                # Handle enter key
                elif char in ['\r', '\n']:
                    print()  # New line for clean output
                    return input_buffer.strip()
                
                # Handle backspace
                elif char in ['\x7f', '\x08']:
                    if input_buffer:
                        input_buffer = input_buffer[:-1]
                        print('\b \b', end='', flush=True)
                
                # Handle Ctrl+C
                elif char == '\x03':
                    raise KeyboardInterrupt
                
                # Handle regular characters
                elif ord(char) >= 32:  # Printable characters
                    input_buffer += char
                    print(char, end='', flush=True)
                    
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def select_book_from_folder(self):
        """Select book from current folder"""
        # Find all .txt and .md files
        txt_files = glob.glob("*.txt")
        md_files = glob.glob("*.md")
        all_files = txt_files + md_files
        
        if not all_files:
            print("\n" + "="*60)
            print(".txt/md Is All You Need - Simple Edition")
            print("="*60)
            print("No .txt or .md files found in current folder.")
            print("Please place some .txt or .md files here and try again.")
            print("\nExample files you can try:")
            print("- Download from Project Gutenberg (gutenberg.org)")
            print("- Create your own .txt file")
            print("- Download from Aozora Bunko (aozora.gr.jp)")
            print("="*60)
            return None
        
        # Sort files alphabetically
        all_files.sort()
        
        files_per_page = 15
        current_page = 0
        
        while True:
            # Calculate page boundaries
            start_idx = current_page * files_per_page
            end_idx = min(start_idx + files_per_page, len(all_files))
            page_files = all_files[start_idx:end_idx]
            
            # Display current page
            print("\n" + "="*60)
            print(".txt/md Is All You Need - Simple Edition")
            print("="*60)
            print("Select a book to read:\n")
            
            for i, filename in enumerate(page_files, start_idx + 1):
                file_size = os.path.getsize(filename)
                size_kb = file_size // 1024
                print(f"{i:2d}. {filename} ({size_kb} KB)")
            
            print()
            total_pages = (len(all_files) + files_per_page - 1) // files_per_page
            print(f"Page {current_page + 1}/{total_pages} | Total: {len(all_files)} files")
            
            if total_pages > 1:
                print("Commands: number = select file, 'n' = next page, 'p' = prev page, filename = direct select")
            else:
                print("Commands: number = select file, filename = direct select")
            
            print("="*60)
            
            choice = input("Your choice: ").strip()
            
            # Handle pagination
            if choice.lower() == 'n' and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice.lower() == 'p' and current_page > 0:
                current_page -= 1
                continue
            
            # Handle number selection
            try:
                num = int(choice)
                if 1 <= num <= len(all_files):
                    return all_files[num - 1]
                else:
                    print(f"Please enter 1-{len(all_files)}")
                    input("Press Enter to continue...")
                    continue
            except ValueError:
                pass
            
            # Handle filename selection
            if choice in all_files:
                return choice
            
            # Handle partial filename match
            matches = [f for f in all_files if choice.lower() in f.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"Multiple matches found: {', '.join(matches)}")
                input("Press Enter to continue...")
                continue
            
            print("Invalid selection. Try again.")
            input("Press Enter to continue...")
    
    def load_book(self):
        """Load book with encoding detection"""
        try:
            encodings = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp']
            
            for encoding in encodings:
                try:
                    with open(self.book_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            return None
            
        except FileNotFoundError:
            return None
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                book_name TEXT NOT NULL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reading_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                note TEXT NOT NULL,
                book_name TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_chat(self, user_msg, ai_response):
        """Save chat to database"""
        if not self.has_api:
            return
            
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO chat_history (timestamp, user_message, ai_response, book_name)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_msg, ai_response, self.book_name))
        conn.commit()
        conn.close()
    
    def save_note(self, note):
        """Save reading note"""
        if not self.has_api:
            # Save to simple text file if no database
            notes_file = f"{self.book_name}_notes.txt"
            with open(notes_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {note}\n")
            return notes_file
        
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO reading_notes (timestamp, note, book_name)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), note, self.book_name))
        conn.commit()
        conn.close()
        return None
    
    def ask_ai(self, user_message):
        """Ask AI using current context"""
        if not self.has_api:
            return "AI features require GEMINI_API_KEY environment variable."
        
        # Get current context
        context_start = max(0, self.current_line - 5)
        context_end = min(len(self.book_lines), self.current_line + self.lines_per_page + 5)
        context_text = '\n'.join(self.book_lines[context_start:context_end])
        
        context = f"""
Book: {self.book_name}
Current context (around line {self.current_line + 1}):
{context_text}

User question: {user_message}
"""
        
        try:
            response = self.gemini_model.generate_content(context)
            ai_response = response.text
            ai_response += "\n\n* AI response - please verify important information"
            
            self.save_chat(user_message, ai_response)
            return ai_response
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "API usage limit reached. Please try again later."
            elif "key" in error_msg.lower():
                return "API key issue. Please check your GEMINI_API_KEY."
            else:
                return f"AI error: {error_msg}"
    
    def search_text(self, query):
        """Search for text in book"""
        results = []
        for i, line in enumerate(self.book_lines):
            if query.lower() in line.lower():
                results.append((i+1, line.strip()))
        return results
    
    def export_simple(self):
        """Export data in simple format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.book_name}_{timestamp}_export.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Reading Session: {self.book_name}\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            if self.has_api:
                # Get data from database
                conn = sqlite3.connect(self.db_path)
                
                chat_cursor = conn.execute('''
                    SELECT timestamp, user_message, ai_response FROM chat_history 
                    WHERE book_name = ? ORDER BY timestamp
                ''', (self.book_name,))
                chats = chat_cursor.fetchall()
                
                notes_cursor = conn.execute('''
                    SELECT timestamp, note FROM reading_notes 
                    WHERE book_name = ? ORDER BY timestamp
                ''', (self.book_name,))
                notes = notes_cursor.fetchall()
                
                conn.close()
                
                f.write("AI CONVERSATIONS\n")
                f.write("-"*20 + "\n")
                for timestamp, user_msg, ai_response in chats:
                    f.write(f"\n[{timestamp.split('T')[0]} {timestamp.split('T')[1][:8]}]\n")
                    f.write(f"Q: {user_msg}\n")
                    f.write(f"A: {ai_response}\n")
                
                f.write("\n\nREADING NOTES\n")
                f.write("-"*20 + "\n")
                for timestamp, note in notes:
                    f.write(f"[{timestamp.split('T')[0]} {timestamp.split('T')[1][:8]}] {note}\n")
            else:
                # Try to read notes from text file
                notes_file = f"{self.book_name}_notes.txt"
                if os.path.exists(notes_file):
                    f.write("READING NOTES\n")
                    f.write("-"*20 + "\n")
                    with open(notes_file, 'r', encoding='utf-8') as nf:
                        f.write(nf.read())
                else:
                    f.write("No notes saved in this session.\n")
        
        return filename
    
    def go_to_next_page(self):
        """Navigate to next page"""
        if self.current_line + self.lines_per_page < len(self.book_lines):
            self.current_line += self.lines_per_page
            self.display_book()
            return True
        else:
            print("\n[End of book]")
            return False
    
    def go_to_prev_page(self):
        """Navigate to previous page"""
        if self.current_line >= self.lines_per_page:
            self.current_line -= self.lines_per_page
            self.display_book()
            return True
        elif self.current_line > 0:
            self.current_line = 0
            self.display_book()
            return True
        else:
            print("\n[Beginning of book]")
            return False
    
    def go_to_next_line(self):
        """Navigate to next line"""
        if self.current_line + 1 < len(self.book_lines):
            self.current_line += 1
            self.display_book()
            return True
        else:
            print("\n[End of book]")
            return False
    
    def go_to_prev_line(self):
        """Navigate to previous line"""
        if self.current_line > 0:
            self.current_line -= 1
            self.display_book()
            return True
        else:
            print("\n[Beginning of book]")
            return False
    
    def handle_arrow_input(self, arrow_command):
        """Handle arrow key navigation"""
        if arrow_command == 'ARROW_UP':
            print("↑ Previous page")
            self.go_to_prev_page()
        elif arrow_command == 'ARROW_DOWN':
            print("↓ Next page")
            self.go_to_next_page()
        elif arrow_command == 'ARROW_LEFT':
            print("← Previous line")
            self.go_to_prev_line()
        elif arrow_command == 'ARROW_RIGHT':
            print("→ Next line")
            self.go_to_next_line()
    
    def display_book(self):
        """Display book content"""
        print("\n" + "="*80)
        print(f".txt/md Simple | {self.book_name}")
        if self.has_api:
            print("AI available - type 'ask <question>' to chat")
        else:
            print("Reading mode only (no AI)")
        print("="*80)
        
        # Book content
        end_line = min(self.current_line + self.lines_per_page, len(self.book_lines))
        
        for i in range(self.current_line, end_line):
            line_num = i + 1
            line_text = self.book_lines[i]
            
            # Wrap long lines
            if len(line_text) > 75:
                wrapped = textwrap.fill(line_text, width=75)
                first_line = wrapped.split('\n')[0]
                print(f"{line_num:4d} | {first_line}")
                for extra_line in wrapped.split('\n')[1:]:
                    print(f"     | {extra_line}")
            else:
                print(f"{line_num:4d} | {line_text}")
        
        # Footer
        print("="*80)
        print(f"Lines {self.current_line + 1}-{end_line}/{len(self.book_lines)}")
        print("Navigation: ↑↓ = page, ←→ = line, Enter = next page, help = commands")
        print("="*80)
    
    def show_response(self, title, content, preserve_format=False):
        """Show response or information"""
        print("\n" + "-"*80)
        print(f"{title}:")
        print("-"*80)
        
        if preserve_format:
            # Keep original formatting (for help, etc.)
            print(content)
        else:
            # Wrap content for readability
            wrapped_content = textwrap.fill(content, width=78)
            print(wrapped_content)
        
        print("-"*80)
    
    def handle_command(self, command):
        """Handle commands"""
        command = command.strip().replace('　', ' ')  # Replace full-width space
        
        if not command:
            # Next page
            if self.current_line + self.lines_per_page < len(self.book_lines):
                self.current_line += self.lines_per_page
                self.display_book()
            else:
                print("\n[End of book reached]")
            return True
        
        # Try as line number first
        try:
            line_num = int(command) - 1
            if 0 <= line_num < len(self.book_lines):
                self.current_line = line_num
                self.display_book()
                return True
        except ValueError:
            pass
        
        # Parse command
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        
        if cmd in ['quit', 'q', 'exit']:
            return False
        
        elif cmd == 'ask':
            if not self.has_api:
                self.show_response("Notice", "AI features require GEMINI_API_KEY environment variable.")
                return True
                
            if args:
                print("AI thinking...")
                response = self.ask_ai(args)
                self.show_response("AI Response", response)
            else:
                self.show_response("Usage", "ask <your question about the text>")
        
        elif cmd == 'add':
            if args:
                result = self.save_note(args)
                if result:  # Text file saved
                    self.show_response("Note Saved", f"Added to {result}: {args}")
                else:  # Database saved
                    self.show_response("Note Saved", f"Added: {args}")
            else:
                self.show_response("Usage", "add <your note>")
        
        elif cmd == 'find':
            if args:
                results = self.search_text(args)
                if results:
                    result_text = f"Found '{args}' in {len(results)} places:\n\n"
                    for line_num, text in results[:10]:  # Show first 10 results
                        result_text += f"Line {line_num}: {text[:60]}...\n"
                    if len(results) > 10:
                        result_text += f"\n... and {len(results) - 10} more"
                    self.show_response("Search Results", result_text)
                else:
                    self.show_response("Search Results", f"'{args}' not found")
            else:
                self.show_response("Usage", "find <text to search>")
        
        elif cmd == 'goto':
            try:
                line_num = int(args) - 1
                if 0 <= line_num < len(self.book_lines):
                    self.current_line = line_num
                    self.display_book()
                else:
                    self.show_response("Error", f"Line number must be 1-{len(self.book_lines)}")
            except ValueError:
                self.show_response("Usage", "goto <line number>")
        
        elif cmd == 'export':
            filename = self.export_simple()
            self.show_response("Export Complete", f"Saved to: {filename}")
        
        elif cmd == 'notes':
            if not self.has_api:
                # Try to read from text file
                notes_file = f"{self.book_name}_notes.txt"
                if os.path.exists(notes_file):
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            self.show_response("Your Notes", content)
                        else:
                            self.show_response("Notes", "No notes yet")
                else:
                    self.show_response("Notes", "No notes yet")
                return True
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT timestamp, note FROM reading_notes 
                WHERE book_name = ? ORDER BY timestamp DESC LIMIT 10
            ''', (self.book_name,))
            notes = cursor.fetchall()
            conn.close()
            
            if notes:
                notes_text = ""
                for timestamp, note in notes:
                    date = timestamp.split('T')[0]
                    time = timestamp.split('T')[1][:8]
                    notes_text += f"{date} {time}: {note}\n"
                self.show_response("Recent Notes", notes_text)
            else:
                self.show_response("Notes", "No notes yet")
        
        elif cmd == 'history':
            if not self.has_api:
                self.show_response("Notice", "Chat history requires AI features. Set GEMINI_API_KEY.")
                return True
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute('''
                SELECT timestamp, user_message, ai_response FROM chat_history 
                WHERE book_name = ? ORDER BY timestamp DESC LIMIT 3
            ''', (self.book_name,))
            history = cursor.fetchall()
            conn.close()
            
            if history:
                history_text = ""
                for timestamp, user_msg, ai_response in history:
                    time = timestamp.split('T')[1][:8]
                    history_text += f"{time} Q: {user_msg}\n"
                    history_text += f"{time} A: {ai_response[:100]}...\n\n"
                self.show_response("Recent Questions", history_text)
            else:
                self.show_response("History", "No questions asked yet")
        
        elif cmd in ['help', 'h']:
            help_text = "Commands:\n"
            
            if self.has_api:
                help_text += "ask <question>   - Ask AI about the text\n"
            
            help_text += """add <note>       - Add reading note
find <text>      - Search in book
goto <line>      - Jump to line number
export           - Export notes"""
            
            if self.has_api:
                help_text += " and chat\n"
            else:
                help_text += "\n"
            
            help_text += "notes            - Show your notes\n"
            
            if self.has_api:
                help_text += "history          - Show recent questions\n"
            
            help_text += """help, h          - Show this help
quit, q          - Exit

Navigation:
Enter            - Next page
↑ (Up arrow)     - Previous page
↓ (Down arrow)   - Next page
← (Left arrow)   - Previous line
→ (Right arrow)  - Next line
Line number      - Jump to line"""
            
            if self.has_api:
                help_text += "\n\nExample: ask What is the main theme here?"
            else:
                help_text += "\n\nNote: Set GEMINI_API_KEY for AI features"
            
            self.show_response("Help", help_text, preserve_format=True)
        
        else:
            self.show_response("Error", f"Unknown command: {cmd}\nType 'help' for available commands")
        
        return True
    
    def run(self):
        """Main application loop"""
        print(f"Loading {self.book_name}...")
        if self.has_api:
            print("* Gemini 2.0 Flash API available")
        else:
            print("* Set GEMINI_API_KEY environment variable for AI access")
        input("Press Enter to start...")
        
        # Show initial content
        self.display_book()
        
        try:
            while True:
                try:
                    # Get command input with arrow key support
                    user_input = self.get_input_with_navigation()
                    
                    # Handle arrow keys
                    if user_input.startswith('ARROW_'):
                        self.handle_arrow_input(user_input)
                        continue
                    
                    if not self.handle_command(user_input):
                        break
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
        
        except KeyboardInterrupt:
            print("\nGoodbye!")

def main():
    """Main function"""
    print("""
.txt/md Is All You Need - Simple Edition
A Terminal-First, AI-Powered e-Book Companion

For everyone, everywhere.
""")
    
    # No arguments needed - file browser will handle selection
    reader = SimpleReader()
    reader.run()

if __name__ == "__main__":
    main()
