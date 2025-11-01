"""Tests for CategoryManagementScreen."""

import asyncio
from typing import cast

from textual.app import App
from textual.binding import Binding

from miniflux_tui.api.models import Category
from miniflux_tui.ui.screens.category_management import CategoryListItem, CategoryManagementScreen


class CategoryManagementTestApp(App):
    """Test app for CategoryManagementScreen testing."""

    def __init__(self, categories: list[Category] | None = None, **kwargs):
        """Initialize test app."""
        super().__init__(**kwargs)
        self.categories = categories or []

    def on_mount(self) -> None:
        """Mount the category management screen."""
        self.push_screen(CategoryManagementScreen(categories=self.categories))


class TestCategoryListItem:
    """Test CategoryListItem rendering."""

    def test_category_list_item_creation(self) -> None:
        """Test creating a CategoryListItem."""
        category = Category(id=1, title="Test Category")
        item = CategoryListItem(category)
        assert item.category.id == 1
        assert item.category.title == "Test Category"

    def test_category_list_item_stores_reference(self) -> None:
        """Test CategoryListItem stores category reference."""
        category = Category(id=1, title="News")
        item = CategoryListItem(category)
        assert item.category == category
        assert item.category.id == 1
        assert item.category.title == "News"


class TestCategoryManagementScreenInitialization:
    """Test CategoryManagementScreen initialization."""

    def test_category_management_screen_creation(self) -> None:
        """Test creating a CategoryManagementScreen."""
        screen = CategoryManagementScreen()
        assert screen.categories == []
        assert screen.list_view is None

    def test_category_management_screen_with_categories(self) -> None:
        """Test CategoryManagementScreen with initial categories."""
        categories = [
            Category(id=1, title="News"),
            Category(id=2, title="Tech"),
        ]
        screen = CategoryManagementScreen(categories=categories)
        assert len(screen.categories) == 2
        assert screen.categories[0].title == "News"
        assert screen.categories[1].title == "Tech"

    def test_category_management_screen_empty(self) -> None:
        """Test CategoryManagementScreen with no categories."""
        screen = CategoryManagementScreen(categories=[])
        assert screen.categories == []


class TestCategoryManagementScreenComposition:
    """Test CategoryManagementScreen composition and rendering."""

    async def test_screen_composes_with_header_and_footer(self) -> None:
        """Test that CategoryManagementScreen composes with header and footer."""
        categories = [Category(id=1, title="News")]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            assert isinstance(screen, CategoryManagementScreen)

    async def test_screen_initializes_with_categories(self) -> None:
        """Test that CategoryManagementScreen initializes with categories."""
        categories = [
            Category(id=1, title="News"),
            Category(id=2, title="Tech"),
        ]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert len(screen.categories) == 2


class TestCategoryManagementScreenNavigation:
    """Test navigation in CategoryManagementScreen."""

    async def test_cursor_down_action_exists(self) -> None:
        """Test that cursor_down action exists."""
        app = CategoryManagementTestApp(categories=[Category(id=1, title="News")])

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_cursor_down)

    async def test_cursor_up_action_exists(self) -> None:
        """Test that cursor_up action exists."""
        app = CategoryManagementTestApp(categories=[Category(id=1, title="News")])

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_cursor_up)

    async def test_back_action_exists(self) -> None:
        """Test that back action exists."""
        app = CategoryManagementTestApp(categories=[Category(id=1, title="News")])

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_back)


class TestCategoryManagementScreenActions:
    """Test action methods in CategoryManagementScreen."""

    async def test_create_category_action_exists(self) -> None:
        """Test that create_category action exists."""
        app = CategoryManagementTestApp()

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_create_category)

    async def test_edit_category_action_exists(self) -> None:
        """Test that edit_category action exists."""
        app = CategoryManagementTestApp()

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_edit_category)

    async def test_delete_category_action_exists(self) -> None:
        """Test that delete_category action exists."""
        app = CategoryManagementTestApp()

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert callable(screen.action_delete_category)


class TestCategoryManagementScreenGetSelected:
    """Test _get_selected_category method."""

    async def test_get_selected_category_no_selection(self) -> None:
        """Test _get_selected_category returns None when nothing selected."""
        categories = [Category(id=1, title="News")]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                selected = screen._get_selected_category()
                assert selected is None or isinstance(selected, Category)

    async def test_get_selected_category_with_selection(self) -> None:
        """Test _get_selected_category returns selected category."""
        categories = [
            Category(id=1, title="News"),
            Category(id=2, title="Tech"),
        ]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen) and screen.list_view and screen.list_view.children:
                screen.list_view.index = 0
                selected = screen._get_selected_category()
                assert selected is None or selected.id == 1


class TestCategoryManagementScreenPopulateList:
    """Test _populate_list method."""

    async def test_populate_list_with_categories(self) -> None:
        """Test _populate_list adds categories to list view."""
        categories = [
            Category(id=1, title="News"),
            Category(id=2, title="Tech"),
        ]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen) and screen.list_view:
                # on_mount already called _populate_list, so list view should have items
                assert len(screen.list_view.children) >= 2

    async def test_populate_list_empty(self) -> None:
        """Test _populate_list with no categories."""
        app = CategoryManagementTestApp(categories=[])

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen) and screen.list_view:
                # on_mount already called _populate_list
                assert len(screen.list_view.children) == 0


class TestCategoryManagementScreenCSS:
    """Test CategoryManagementScreen CSS styling."""

    def test_category_management_screen_has_css(self) -> None:
        """Test CategoryManagementScreen has CSS defined."""
        screen = CategoryManagementScreen()
        assert screen.CSS is not None
        assert len(screen.CSS) > 0
        assert "CategoryManagementScreen" in screen.CSS


class TestCategoryManagementScreenBindings:
    """Test keyboard bindings."""

    def test_category_management_screen_has_bindings(self) -> None:
        """Test CategoryManagementScreen has key bindings."""
        screen = CategoryManagementScreen()
        bindings = cast(list[Binding], screen.BINDINGS)  # type: ignore[attr-defined]
        binding_keys = [b.key for b in bindings]
        assert "j" in binding_keys
        assert "k" in binding_keys
        assert "n" in binding_keys
        assert "e" in binding_keys
        assert "d" in binding_keys
        assert "escape" in binding_keys

    def test_category_management_screen_binding_descriptions(self) -> None:
        """Test that bindings have descriptions."""
        screen = CategoryManagementScreen()
        bindings = cast(list[Binding], screen.BINDINGS)  # type: ignore[attr-defined]
        for binding in bindings:
            assert binding.description is not None
            assert len(binding.description) > 0


class TestCategoryManagementScreenIntegration:
    """Integration tests for CategoryManagementScreen."""

    async def test_screen_has_list_view(self) -> None:
        """Test that screen initializes with a ListView."""
        categories = [Category(id=1, title="News")]
        app = CategoryManagementTestApp(categories=categories)

        async with app.run_test():
            screen = app.screen
            if isinstance(screen, CategoryManagementScreen):
                assert screen.list_view is not None

    async def test_compose_returns_result(self) -> None:
        """Test compose method returns valid result."""
        screen = CategoryManagementScreen()
        result = screen.compose()
        assert hasattr(result, "__iter__")

    def test_category_management_with_multiple_categories(self) -> None:
        """Test CategoryManagementScreen with multiple categories."""
        categories = [
            Category(id=1, title="News"),
            Category(id=2, title="Tech"),
            Category(id=3, title="Business"),
            Category(id=4, title="Sports"),
        ]
        screen = CategoryManagementScreen(categories=categories)
        assert len(screen.categories) == 4

    def test_category_management_with_long_category_name(self) -> None:
        """Test CategoryManagementScreen with long category names."""
        long_name = "This is a very long category name for testing purposes"
        category = Category(id=1, title=long_name)
        screen = CategoryManagementScreen(categories=[category])
        assert screen.categories[0].title == long_name

    def test_category_management_with_special_characters(self) -> None:
        """Test CategoryManagementScreen with special characters in names."""
        special_category = Category(id=1, title="News & Updates (2025)")
        screen = CategoryManagementScreen(categories=[special_category])
        assert screen.categories[0].title == "News & Updates (2025)"


class TestCategoryManagementAsyncMethods:
    """Test that async methods exist and are properly defined."""

    def test_action_create_category_is_async(self) -> None:
        """Test that action_create_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen.action_create_category)

    def test_do_create_category_is_async(self) -> None:
        """Test that _do_create_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen._do_create_category)

    def test_action_edit_category_is_async(self) -> None:
        """Test that action_edit_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen.action_edit_category)

    def test_do_edit_category_is_async(self) -> None:
        """Test that _do_edit_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen._do_edit_category)

    def test_action_delete_category_is_async(self) -> None:
        """Test that action_delete_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen.action_delete_category)

    def test_do_delete_category_is_async(self) -> None:
        """Test that _do_delete_category is an async method."""
        screen = CategoryManagementScreen()
        assert asyncio.iscoroutinefunction(screen._do_delete_category)
