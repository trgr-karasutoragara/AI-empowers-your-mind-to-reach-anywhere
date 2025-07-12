#!/usr/bin/env python3
"""
.txt/md Is All You Need
A Terminal-First, AI-Powered e-Book Companion

Repository: txt-md-is-all-you-need

Usage:
    python3 reader.py book.txt

Interface:
    - All history preserved in terminal (no screen clearing)
    - Book content flows continuously
    - AI responses appear inline when called

Commands:
    :ai <message>   - Talk to Gemma 3 1B (local)
    :api <message>  - Talk to Gemini 2.0 Flash (API)
    :add <note>     - Add reading note
    :ftr <text>     - Full text search
    :goto <line>    - Jump to line number
    :exp            - Export data
    :notes          - Show notes
    :history        - Show chat history
    :help, :h       - Show help
    :q              - Exit

Navigation:
    - Enter: Next page
    - ↑ (Up arrow): Previous page
    - ↓ (Down arrow): Next page  
    - ← (Left arrow): Previous line
    - → (Right arrow): Next line
    - Line number + Enter: Jump to line

Required packages:
pip install ollama google-generativeai
"""

import ollama
import sqlite3
import sys
import os
import textwrap
import json
import csv
import termios
import tty
from datetime import datetime

# Optional: Google Generative AI for API support
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class Reader:
    def __init__(self, book_path, db_path=None):
        self.book_path = book_path
        self.book_name = os.path.basename(book_path)
        self.db_path = db_path or f"{self.book_name}_session.db"
        self.model = "gemma3:1b"
        
        # Display settings
        self.lines_per_page = 20
        self.current_line = 0
        
        # API settings
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.setup_gemini_api()
        
        # Load book
        self.book_content = self.load_book()
        if not self.book_content:
            print(f"Error: Could not load {book_path}")
            sys.exit(1)
        
        self.book_lines = self.book_content.split('\n')
        
        self.init_database()
    
    def setup_gemini_api(self):
        """Setup Gemini API if available"""
        if not GEMINI_AVAILABLE:
            self.gemini_available = False
            return
            
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                self.gemini_available = True
            except Exception as e:
                print(f"Warning: Gemini API setup failed: {e}")
                self.gemini_available = False
        else:
            self.gemini_available = False
    
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
    
    def check_ollama(self):
        """Check Ollama connection"""
        try:
            ollama.generate(model=self.model, prompt="test")
            return True
        except:
            return False
    
    def save_chat(self, user_msg, ai_response):
        """Save chat to database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO chat_history (timestamp, user_message, ai_response, book_name)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_msg, ai_response, self.book_name))
        conn.commit()
        conn.close()
    
    def save_note(self, note):
        """Save reading note"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO reading_notes (timestamp, note, book_name)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), note, self.book_name))
        conn.commit()
        conn.close()
    
    def chat_with_ai(self, user_message):
        """Chat with AI using RAG"""
        # Get current context
        context_start = max(0, self.current_line - 5)
        context_end = min(len(self.book_lines), self.current_line + self.lines_per_page + 5)
        context_text = '\n'.join(self.book_lines[context_start:context_end])
        
        context = f"""
Book: {self.book_name}
Current context (around line {self.current_line + 1}):
{context_text}

User message: {user_message}
"""
        
        try:
            response = ollama.generate(model=self.model, prompt=context)
            ai_response = response['response']
            
            # No length restriction - show full response
            ai_response += "\n\n* AI may be wrong. Please verify with libraries."
            
            self.save_chat(user_message, ai_response)
            return ai_response
            
        except Exception as e:
            return f"AI error: {e}"
    
    def chat_with_gemini_api(self, user_message):
        """Chat with Gemini 2.0 Flash via API"""
        if not self.gemini_available:
            return "Gemini API not available. Set GEMINI_API_KEY environment variable."
        
        # Get current context
        context_start = max(0, self.current_line - 5)
        context_end = min(len(self.book_lines), self.current_line + self.lines_per_page + 5)
        context_text = '\n'.join(self.book_lines[context_start:context_end])
        
        context = f"""
Book: {self.book_name}
Current context (around line {self.current_line + 1}):
{context_text}

User message: {user_message}
"""
        
        try:
            response = self.gemini_model.generate_content(context)
            api_response = response.text
            
            # No length restriction - show full response
            api_response += "\n\n* Gemini 2.0 Flash via API"
            
            self.save_chat(f"[API] {user_message}", api_response)
            return api_response
            
        except Exception as e:
            return f"Gemini API error: {e}"
    
    def full_text_search(self, query):
        """Full text search returning line numbers"""
        results = []
        for i, line in enumerate(self.book_lines):
            if query.lower() in line.lower():
                results.append((i+1, line.strip()))
        return results
    
    def export_data(self, format_choice):
        """Export data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{self.book_name}_{timestamp}"
        
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
        
        if format_choice == 1:  # CSV
            filename = f"{base_name}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Type', 'Timestamp', 'Content', 'AI_Response'])
                
                for timestamp, user_msg, ai_response in chats:
                    writer.writerow(['Chat', timestamp, user_msg, ai_response])
                
                for timestamp, note in notes:
                    writer.writerow(['Note', timestamp, note, ''])
            
        elif format_choice == 2:  # JSON
            filename = f"{base_name}.json"
            data = {
                'book': self.book_name,
                'export_time': datetime.now().isoformat(),
                'chats': [{'timestamp': t, 'user': u, 'ai': a} for t, u, a in chats],
                'notes': [{'timestamp': t, 'note': n} for t, n in notes]
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        elif format_choice == 3:  # Markdown
            filename = f"{base_name}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Reading Session: {self.book_name}\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Chat History\n\n")
                for timestamp, user_msg, ai_response in chats:
                    f.write(f"### {timestamp}\n")
                    f.write(f"**You:** {user_msg}\n\n")
                    f.write(f"**AI:** {ai_response}\n\n")
                
                f.write("## Notes\n\n")
                for timestamp, note in notes:
                    f.write(f"- **{timestamp}:** {note}\n")
            
        elif format_choice == 4:  # TXT
            filename = f"{base_name}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Reading Session: {self.book_name}\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*50 + "\n\n")
                
                f.write("CHAT HISTORY\n")
                f.write("-"*20 + "\n")
                for timestamp, user_msg, ai_response in chats:
                    f.write(f"\n[{timestamp}]\n")
                    f.write(f"You: {user_msg}\n")
                    f.write(f"AI: {ai_response}\n")
                
                f.write("\n\nNOTES\n")
                f.write("-"*20 + "\n")
                for timestamp, note in notes:
                    f.write(f"\n[{timestamp}] {note}\n")
        
        return filename
    
    def clear_screen(self):
        """Clear screen - DISABLED for history preservation"""
        pass  # Keep all history in terminal
    
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
    
    def display_book(self):
        """Display book content - PRESERVE HISTORY"""
        # Don't clear screen - keep history
        
        # Header
        print("\n" + "="*80)
        print(f".txt/md Is All You Need | {self.book_name}")
        print("="*80)
        
        # Book content - CENTER FOCUS
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
        print("Navigation: ↑↓ = page, ←→ = line, Enter = next page, :h = help")
        print("="*80)
    
    def show_ai_response(self, response):
        """Show AI response at bottom - PRESERVE HISTORY"""
        print("\n" + "-"*80)
        print("AI Response:")
        print("-"*80)
        
        # Wrap AI response for better readability, but show everything
        wrapped_response = textwrap.fill(response, width=78)
        print(wrapped_response)
        
        print("-"*80)
        print(f"Response length: {len(response)} characters")
        print("-"*80)
    
    def show_info(self, title, content):
        """Show information - PRESERVE HISTORY"""
        print("\n" + "-"*80)
        print(f"{title}:")
        print("-"*80)
        print(content)
        print("-"*80)
    
    def handle_command(self, command):
        """Handle vim-style commands"""
        if not command.startswith(':'):
            return True
        
        command = command[1:]  # Remove ':'
        
        # Clean up command (remove extra spaces, handle full-width characters)
        command = command.replace('　', ' ')  # Replace full-width space
        command = command.strip()
        
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        
        if cmd == 'q' or cmd == 'quit':
            return False
        
        elif cmd == 'ai':
            if args:
                print("AI thinking...")
                response = self.chat_with_ai(args)
                self.show_ai_response(response)
            else:
                self.show_info("Usage", ":ai <question for AI>")
        
        elif cmd == 'api':
            if args:
                print("Gemini API thinking...")
                response = self.chat_with_gemini_api(args)
                self.show_ai_response(response)
            else:
                self.show_info("Usage", ":api <question for Gemini 2.0 Flash>")
        
        elif cmd == 'add':
            if args:
                self.save_note(args)
                self.show_info("Note Saved", f"Added: {args}")
            else:
                self.show_info("Usage", ":add <note content>")
        
        elif cmd == 'ftr':
            if args:
                results = self.full_text_search(args)
                if results:
                    result_text = f"Found '{args}' in {len(results)} places:\n\n"
                    for line_num, text in results[:15]:
                        result_text += f"Line {line_num}: {text[:50]}...\n"
                    self.show_info("Search Results", result_text)
                else:
                    self.show_info("Search Results", f"'{args}' not found")
            else:
                self.show_info("Usage", ":ftr <search text>")
        
        elif cmd == 'goto':
            try:
                line_num = int(args) - 1
                if 0 <= line_num < len(self.book_lines):
                    self.current_line = line_num
                    self.display_book()
                else:
                    self.show_info("Error", f"Line number must be 1-{len(self.book_lines)}")
            except ValueError:
                self.show_info("Usage", ":goto <line number>")
        
        elif cmd == 'exp':
            print("\nExport Format:")
            print("1. CSV")
            print("2. JSON") 
            print("3. Markdown")
            print("4. Text")
            choice = input("Please select 1, 2, 3, or 4: ").strip()
            
            if choice in ['1', '2', '3', '4']:
                filename = self.export_data(int(choice))
                self.show_info("Export Complete", f"Saved to: {filename}")
            else:
                self.show_info("Notice", "Please choose 1, 2, 3, or 4")
        
        elif cmd == 'notes':
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
                self.show_info("Recent Notes", notes_text)
            else:
                self.show_info("Notes", "No notes yet")
        
        elif cmd == 'history':
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
                    # Show full content, no truncation
                    history_text += f"{time} You: {user_msg}\n"
                    history_text += f"{time} AI: {ai_response}\n\n"
                self.show_info("Recent Chat", history_text)
            else:
                self.show_info("History", "No chat history")
        
        elif cmd == 'help' or cmd == 'h':  # Support both :help and :h
            help_text = """Commands:
:ai <question>    - Ask Gemma 3 1B (local)
:api <question>   - Ask Gemini 2.0 Flash (API)
:add <note>       - Add reading note
:ftr <text>       - Search in book
:goto <line>      - Jump to line number
:exp              - Export data
:notes            - Show notes
:history          - Show chat history
:help, :h         - Show this help
:q                - Quit

Navigation:
- Enter: Next page
- ↑ (Up arrow): Previous page
- ↓ (Down arrow): Next page  
- ← (Left arrow): Previous line
- → (Right arrow): Next line
- Line number + Enter: Jump to line"""
            self.show_info("Help", help_text)

        
        else:
            # Try as line number
            try:
                line_num = int(cmd) - 1
                if 0 <= line_num < len(self.book_lines):
                    self.current_line = line_num
                    self.display_book()
                else:
                    self.show_info("Error", f"Line number must be 1-{len(self.book_lines)}")
            except ValueError:
                self.show_info("Error", f"Unknown command: :{cmd}\nType :h for commands")
        
        return True
    
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
    
    def run(self):
        """Main application loop"""
        if not self.check_ollama():
            print("Error: Ollama not available")
            print("Make sure Ollama is running with gemma3:1b")
            return
        
        print(f"Loading {self.book_name}...")
        print("* AI may be wrong. Please verify with libraries.")
        print("* Use arrow keys for navigation: ↑↓ for pages, ←→ for lines")
        if self.gemini_available:
            print("* Gemini 2.0 Flash API available (:api command)")
        else:
            print("* Set GEMINI_API_KEY environment variable for API access")
        input("Press Enter to start...")
        
        # Show initial content
        self.display_book()
        
        try:
            while True:
                # Get command input with arrow key support
                try:
                    user_input = self.get_input_with_navigation()
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                
                # Handle arrow keys
                if user_input.startswith('ARROW_'):
                    self.handle_arrow_input(user_input)
                    continue
                
                if not user_input:
                    # Next page (Enter key)
                    print("Enter - Next page")
                    self.go_to_next_page()
                    continue
                
                if not self.handle_command(user_input):
                    break
        
        except KeyboardInterrupt:
            print("\nGoodbye!")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("""
.txt/md Is All You Need
A Terminal-First, AI-Powered e-Book Companion

Usage:
    python3 reader.py book.txt

Environment Variables:
    GEMINI_API_KEY    - For Gemini 2.0 Flash API access

Repository: txt-md-is-all-you-need
""")
        sys.exit(1)
    
    book_path = sys.argv[1]
    reader = Reader(book_path)
    reader.run()

if __name__ == "__main__":
    main()
