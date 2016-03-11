import sublime
import sublime_plugin


class Todoodle(sublime_plugin.TextCommand):
    def gather_all(self):
        return self.view.find_by_selector('todoodle.item')

    def cursor(self):
        try:
            return self.view.sel()[0].a
        except IndexError:
            return 0

    def select_item(self, index):
        todos = self.gather_all()
        if len(todos) == 0:
            return

        try:
            todo = todos[index]
            item = sublime.Region(todo.begin(), todo.begin() + 3)
            self.view.sel().add(item)
        except IndexError:
            pass

    def current(self):
        todos = self.gather_all()
        if len(todos) == 0:
            return
        current = None
        cursor = self.cursor()
        for (index, region) in enumerate(todos):
            if region.contains(cursor):
                current = index
                break

        return current

    def next_nearest(self):
        todos = self.gather_all()
        if len(todos) == 0:
            return

        next_nearest = None
        prev_dist = None
        cursor = self.cursor()
        for (index, region) in enumerate(todos):
            if region.begin() > cursor:
                dist = region.begin() - cursor
                if prev_dist is None or dist < prev_dist:
                    next_nearest = index
                    prev_dist = dist
        return next_nearest

    def prev_nearest(self):
        todos = self.gather_all()
        if len(todos) == 0:
            return

        prev_nearest = None
        prev_dist = None
        cursor = self.cursor()
        for (index, region) in enumerate(todos):
            if region.begin() < cursor:
                dist = cursor - region.begin()
                if prev_dist is None or dist < prev_dist:
                    prev_nearest = index
                    prev_dist = dist
        return prev_nearest

class TodoodleSelectItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0:
            return

        delta = kwargs.get('delta', 0)
        if current is None:
            if delta > 0:
                current = self.next_nearest()
            else:
                current = self.prev_nearest()
        else:
            current = (current + delta) % len(todos)

        if current is not None:
            self.view.sel().clear()
            self.view.sel().add(self.select_item(current))


class TodoodleMoveItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        delta = kwargs.get('delta', 0)
        other = current + delta
        if other < 0 or other >= len(todos) or other == current:
            return

        current_reg = self.view.line(todos[current].begin())
        other_reg = self.view.line(todos[other].begin())

        current_text = self.view.substr(current_reg)
        other_text = self.view.substr(other_reg)

        if current < other:
            self.view.replace(edit, other_reg, current_text)
            self.view.replace(edit, current_reg, other_text)
        else:
            self.view.replace(edit, current_reg, other_text)
            self.view.replace(edit, other_reg, current_text)
        self.view.run_command('todoodle_select_item', {'delta': delta})


class TodoodleToggleItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        next_status = kwargs.get('status', '✓')
        current_reg = todos[current]
        todo = self.view.substr(current_reg)
        status = todo[1:2]
        if status == next_status:
            self.view.run_command('todoodle_set_item_status', {'status': ' '})
        else:
            self.view.run_command('todoodle_set_item_status', {'status': next_status})


class TodoodleSetItemStatusCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        status = kwargs.get('status', '✓')
        current_reg = todos[current]
        todo = self.view.substr(current_reg)
        todo = "[" + status + "] " + todo[4:]
        self.view.replace(edit, current_reg, todo)


class TodoodleIndentItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        current_reg = todos[current]
        self.view.insert(edit, current_reg.begin(), '    ')


class TodoodleUnindentItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        current_reg = todos[current]
        line = self.view.line(current_reg)
        indent_len = 4
        if line.begin() <= current_reg.begin() - indent_len:
            unindent = sublime.Region(current_reg.begin() - indent_len, current_reg.begin())
            self.view.replace(edit, unindent, '')


class TodoodleCreateItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        cursor = self.view.sel()[0]
        line = self.view.line(cursor.begin())
        indent = cursor.begin() - line.begin()
        spaces = self.view.substr(sublime.Region(line.begin(), cursor.begin()))

        if spaces == ' ' * indent:
            self.view.replace(edit, cursor, '[ ] ')
            self.view.sel().clear()
            self.view.sel().add(cursor.end() + 4)
        else:
            plus = kwargs.get('key', '+')
            self.view.insert(edit, cursor.end(), plus)


class TodoodleCreateNextItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            return

        line = self.view.line(todos[current])
        indent = ' ' * (todos[current].begin() - line.begin())
        insert = "\n" + indent + "[ ] "
        self.view.insert(edit, line.end(), insert)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(line.end() + len(insert), line.end() + len(insert)))

    def create_todo(self, todo):
        self.view.run_command('todoodle_replace_item', {'todo': todo})

class TodoodleEditItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        current_reg = todos[current]
        todo_reg = sublime.Region(current_reg.begin() + 4, current_reg.end())
        todo = self.view.substr(todo_reg)
        self.view.window().show_input_panel('Update:', todo, self.update_todo, self.update_todo, None)

    def update_todo(self, todo):
        self.view.run_command('todoodle_replace_item', {'todo': todo})


class TodoodleReplaceItemCommand(Todoodle):
    def run(self, edit, todo):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        current_reg = todos[current]
        todo_reg = sublime.Region(current_reg.begin() + 4, current_reg.end())
        self.view.replace(edit, todo_reg, todo)

        self.view.run_command('todoodle_select_item', {'delta': 0})

class TodoodleDeleteItemCommand(Todoodle):
    def run(self, edit, **kwargs):
        todos = self.gather_all()
        current = self.current()
        if len(todos) == 0 or current is None:
            self.view.run_command('todoodle_select_item', {'delta': 1})
            return

        current_reg = todos[current]
        line = self.view.full_line(current_reg)
        self.view.replace(edit, line, '')
        self.view.run_command('todoodle_select_item', {'delta': 0})
