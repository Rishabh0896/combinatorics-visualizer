import math

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
import itertools
from numpy import linspace


class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.symbol = self.get_symbol()
        self.color = 'red' if suit in ['♥', '♦'] else 'black'

    def get_symbol(self):
        if self.value == 1:
            return 'A'
        elif self.value == 11:
            return 'J'
        elif self.value == 12:
            return 'Q'
        elif self.value == 13:
            return 'K'
        return str(self.value)

    def __str__(self):
        return f"{self.symbol}{self.suit}"


def create_deck(n):
    """Create a deck with n cards, cycling through suits and values"""
    suits = ['♥', '♠', '♣', '♦']
    values = list(range(1, 14))  # 1-13 for A-K
    cards = []

    for i in range(n):
        suit = suits[i % len(suits)]
        value = values[i % len(values)]
        cards.append(Card(value, suit))

    return cards


def create_card_patch(ax, card, x, y, width=0.6, height=0.8):
    """Create a playing card visualization"""
    card_patch = patches.Rectangle((x, y), width, height, facecolor='white',
                                   edgecolor='black', linewidth=1, zorder=1)
    ax.add_patch(card_patch)

    text_color = card.color
    ax.text(x + width / 2, y + height / 2, f"{card.symbol}\n{card.suit}",
            ha='center', va='center', color=text_color,
            fontsize=10, fontweight='bold', zorder=2)


def calculate_grid_dimensions(n_arrangements):
    """Calculate optimal grid dimensions based on number of arrangements"""
    if n_arrangements <= 4:
        return 1, n_arrangements
    elif n_arrangements <= 8:
        return 2, 4
    else:
        n_cols = min(6, n_arrangements)
        n_rows = (n_arrangements + n_cols - 1) // n_cols
        return n_rows, n_cols


def create_grid_display(arrangements, arrangement_type):
    """Create a grid display of all arrangements with dynamic sizing"""
    n_arrangements = len(arrangements)
    n_rows, n_cols = calculate_grid_dimensions(n_arrangements)

    # Calculate figure size based on number of arrangements
    width = min(15, n_cols * 3)
    height = min(15, n_rows * 2)

    fig = plt.figure(figsize=(width, height))
    fig.suptitle(f"All {arrangement_type} Arrangements", y=1.02, fontsize=16, fontweight='bold')

    for idx, arrangement in enumerate(arrangements):
        ax = fig.add_subplot(n_rows, n_cols, idx + 1)

        # Adjust xlim based on number of cards in arrangement
        xlim_width = max(4, int(len(arrangement) * 0.8))
        ax.set_xlim(-xlim_width / 2, xlim_width / 2)
        ax.set_ylim(0, 2)
        ax.axis('off')

        # Center the cards
        start_x = -((len(arrangement) - 1) * 0.7) / 2
        for i, card in enumerate(arrangement):
            create_card_patch(ax, card, start_x + i * 0.7, 0.5)

        ax.set_title(f"#{idx + 1}", fontsize=10)

    plt.tight_layout()
    return fig


def animate_card_selection(cards, r, selection_type, delay=0.2):
    """Animate card selection with dynamic number of cards and positions"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8),
                                   gridspec_kw={'height_ratios': [1, 2]})
    plt.close()

    # Calculate card positions for deck display
    n_cards = len(cards)
    deck_width = n_cards * 0.7
    start_x = -deck_width / 2

    # Setup deck area with dynamic width
    ax1.set_xlim(start_x - 0.5, start_x + deck_width + 0.5)
    ax1.set_ylim(0, 2)
    ax1.axis('off')
    ax1.set_title("Available Cards")

    # Setup selection area
    ax2.set_xlim(-(r * 0.7) / 2 - 0.5, (r * 0.7) / 2 + 0.5)
    ax2.set_ylim(0, 2)
    ax2.axis('off')
    ax2.set_title("Selected Cards")

    # Initial deck display
    for i, card in enumerate(cards):
        create_card_patch(ax1, card, start_x + i * 0.7, 0.5)

    plot_container = st.empty()
    plot_container.pyplot(fig)
    time.sleep(delay)

    # Generate arrangements based on selection type
    if selection_type == "Permutation (No Repetition)":
        arrangements = list(itertools.permutations(cards, r))
    elif selection_type == "Permutation (With Repetition)":
        arrangements = list(itertools.product(cards, repeat=r))
    elif selection_type == "Combination (No Repetition)":
        arrangements = list(itertools.combinations(cards, r))
    else:  # Combination with Repetition
        arrangements = list(itertools.combinations_with_replacement(cards, r))

    # Progress tracking
    progress_bar = st.progress(0)
    info_container = st.empty()

    # Animate each arrangement
    for arr_idx, arrangement in enumerate(arrangements):
        progress_bar.progress((arr_idx + 1) / len(arrangements))

        # Animation for each card in the arrangement
        for i, card in enumerate(arrangement):
            for y in linspace(2, 0.5, 3):
                ax2.clear()
                ax2.set_xlim(-(r * 0.7) / 2 - 0.5, (r * 0.7) / 2 + 0.5)
                ax2.set_ylim(0, 2)
                ax2.axis('off')
                ax2.set_title(f"Arrangement {arr_idx + 1} of {len(arrangements)}")

                # Show previously placed cards
                start_x_arr = -(r * 0.7) / 2
                for j in range(i):
                    create_card_patch(ax2, arrangement[j], start_x_arr + j * 0.7, 0.5)

                # Show current card being placed
                create_card_patch(ax2, card, start_x_arr + i * 0.7, y)

                plot_container.pyplot(fig)
                plt.close()
                time.sleep(0.01)

        # Show final arrangement
        ax2.clear()
        ax2.set_xlim(-(r * 0.7) / 2 - 0.5, (r * 0.7) / 2 + 0.5)
        ax2.set_ylim(0, 2)
        ax2.axis('off')
        ax2.set_title(f"Arrangement {arr_idx + 1} of {len(arrangements)}")

        start_x_arr = -(r * 0.7) / 2
        for i, card in enumerate(arrangement):
            create_card_patch(ax2, card, start_x_arr + i * 0.7, 0.5)

        plot_container.pyplot(fig)
        plt.close()
        info_container.write(f"Arrangement {arr_idx + 1}: {' '.join(str(card) for card in arrangement)}")
        time.sleep(delay)

    return arrangements


def calculate_comparison_layout(arrangements_dict):
    """Calculate optimal layout parameters based on number of arrangements"""
    max_arrangements = max(len(arr) for arr in arrangements_dict.values())

    # Calculate number of columns based on total arrangements
    if max_arrangements <= 3:
        cols = max_arrangements
    elif max_arrangements <= 6:
        cols = 3
    else:
        cols = 4

    # Calculate rows needed for each quadrant
    rows = math.ceil(max_arrangements / cols)

    # Calculate scaling factors
    ax_width = min(0.28, 0.9 / cols)  # Scale width based on columns
    ax_height = min(0.28, 0.8 / rows)  # Scale height based on rows

    # Calculate spacing
    x_spacing = min(0.32, 1.0 / cols)
    y_spacing = min(0.32, 0.9 / rows)

    return cols, rows, ax_width, ax_height, x_spacing, y_spacing


def create_responsive_comparison_view(cards, r):
    """
    Create a responsive grid showing all arrangement types that scales with the window size
    """
    types = [
        "Permutation (No Repetition)",
        "Permutation (With Repetition)",
        "Combination (No Repetition)",
        "Combination (With Repetition)"
    ]

    arrangements_dict = {
        "Permutation (No Repetition)": list(itertools.permutations(cards, r)),
        "Permutation (With Repetition)": list(itertools.product(cards, repeat=r)),
        "Combination (No Repetition)": list(itertools.combinations(cards, r)),
        "Combination (With Repetition)": list(itertools.combinations_with_replacement(cards, r))
    }

    st.write(f"### Comparison of All Arrangement Types (n={len(cards)}, r={r})")

    # Create a 2x2 grid using Streamlit columns
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)

    # Helper function to create card visualization
    def create_arrangement_display(arrangements, container, title):
        with container:
            st.write(f"#### {title}")
            st.write(f"Total arrangements: {len(arrangements)}")

            # Create figure with dynamic sizing based on number of arrangements
            n_arrangements = len(arrangements)
            cols = min(4, n_arrangements)
            rows = math.ceil(n_arrangements / cols)

            # Calculate figure size based on content
            width = min(12, cols * 3)
            height = min(12, rows * 2.5)

            fig = plt.figure(figsize=(width, height))

            for idx, arrangement in enumerate(arrangements):
                ax = fig.add_subplot(rows, cols, idx + 1)

                # Scale card size based on number of cards
                card_width = 0.7 / max(len(arrangement), 3)
                card_spacing = card_width * 1.2
                total_width = card_spacing * (len(arrangement) - 1)

                # Set axis limits with margins
                margin = card_width
                ax.set_xlim(-total_width / 2 - margin, total_width / 2 + margin)
                ax.set_ylim(-0.2, 1.2)
                ax.axis('off')

                # Draw cards
                start_x = -total_width / 2
                for i, card in enumerate(arrangement):
                    create_card_patch(ax, card,
                                      start_x + i * card_spacing,
                                      0.2,
                                      width=card_width,
                                      height=card_width * 1.4)

                ax.set_title(f"#{idx + 1}", fontsize=8, pad=2)

            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    # Display each arrangement type in its quadrant
    for i, (type_name, arrangements) in enumerate(arrangements_dict.items()):
        if i < 2:
            create_arrangement_display(arrangements, row1_cols[i], type_name)
        else:
            create_arrangement_display(arrangements, row2_cols[i - 2], type_name)

    # Add explanation and formulas
    st.write("### Key Formulas")

    formulas = {
        "Permutation (No Repetition)": {
            "formula": f"P(n,r) = P({len(cards)},{r}) = {len(cards)}!/{(len(cards) - r)}!",
            "result": math.perm(len(cards), r)
        },
        "Permutation (With Repetition)": {
            "formula": f"n^r = {len(cards)}^{r}",
            "result": len(cards) ** r
        },
        "Combination (No Repetition)": {
            "formula": f"C(n,r) = C({len(cards)},{r}) = {len(cards)}!/({r}!*{len(cards) - r}!)",
            "result": math.comb(len(cards), r)
        },
        "Combination (With Repetition) - Balls and Bins": {
            "formula": f"C(balls + bins - 1, bins - 1) = C({len(cards) + r - 1},{r})",
            "result": math.comb(len(cards) + r - 1, r)
        }
    }

    # Create formula comparison using Streamlit columns
    formula_cols = st.columns(2)

    for i, (type_name, formula_data) in enumerate(formulas.items()):
        col = formula_cols[i % 2]
        with col:
            st.write(f"**{type_name}**")
            st.latex(formula_data["formula"] + f" = {formula_data['result']}")

    return arrangements_dict


def create_comparison_view(cards, r):
    """Create a grid showing all four types of arrangements side by side with dynamic scaling"""
    types = [
        "Permutation (No Repetition)",
        "Permutation (With Repetition)",
        "Combination (No Repetition)",
        "Combination (With Repetition)"
    ]

    arrangements_dict = {
        "Permutation (No Repetition)": list(itertools.permutations(cards, r)),
        "Permutation (With Repetition)": list(itertools.product(cards, repeat=r)),
        "Combination (No Repetition)": list(itertools.combinations(cards, r)),
        "Combination (With Repetition)": list(itertools.combinations_with_replacement(cards, r))
    }

    # Calculate layout parameters
    cols, rows, ax_width, ax_height, x_spacing, y_spacing = calculate_comparison_layout(arrangements_dict)

    # Calculate figure size based on arrangements
    max_arrangements = max(len(arr) for arr in arrangements_dict.values())
    base_height = 10  # Minimum height
    height_per_row = 2  # Additional height per row
    fig_height = min(24, max(base_height, base_height + (rows - 2) * height_per_row))

    # Create figure
    fig = plt.figure(figsize=(20, fig_height))

    # Add main title
    fig.suptitle(f"Comparison of All Arrangement Types (n={len(cards)}, r={r})",
                 fontsize=20, y=0.98, fontweight='bold')

    # Create main dividing lines with adjusted positions
    line_positions = {
        'vertical': {'x': 0.5, 'y1': 0.08, 'y2': 0.92},
        'horizontal': {'x1': 0.08, 'x2': 0.92, 'y': 0.5}
    }

    # Add dividing lines
    line1 = plt.Line2D([line_positions['vertical']['x']] * 2,
                       [line_positions['vertical']['y1'], line_positions['vertical']['y2']],
                       transform=fig.transFigure,
                       color='black',
                       linewidth=2)
    line2 = plt.Line2D([line_positions['horizontal']['x1'], line_positions['horizontal']['x2']],
                       [line_positions['horizontal']['y']] * 2,
                       transform=fig.transFigure,
                       color='black',
                       linewidth=2)
    fig.add_artist(line1)
    fig.add_artist(line2)

    # Create a 2x2 grid for the main types
    for idx, arrangement_type in enumerate(types, 1):
        arrangements = arrangements_dict[arrangement_type]
        n_arrangements = len(arrangements)

        main_ax = plt.subplot(2, 2, idx)
        main_ax.set_title(f"{arrangement_type}\n(Total: {n_arrangements})",
                          fontsize=14, pad=20, fontweight='bold')
        main_ax.axis('off')

        # Calculate actual rows and columns needed for this arrangement type
        actual_rows = math.ceil(n_arrangements / cols)

        # Draw arrangements for this type
        for arr_idx, arrangement in enumerate(arrangements):
            row = arr_idx // cols
            col = arr_idx % cols

            # Calculate position with scaled spacing
            x_pos = 0.05 + (col * x_spacing)
            y_pos = 0.8 - (row * y_spacing)

            # Create subplot for this arrangement
            ax = fig.add_axes([
                main_ax.get_position().x0 + x_pos * main_ax.get_position().width,
                main_ax.get_position().y0 + y_pos * main_ax.get_position().height,
                ax_width * main_ax.get_position().width,
                ax_height * main_ax.get_position().height
            ])

            # Calculate card scaling
            card_width = 0.7 / max(r, 3)  # Scale card width based on number of cards
            card_spacing = card_width * 1.3  # Scale spacing based on card width
            total_width = card_spacing * (r - 1)  # Total width of arrangement

            # Adjust xlim based on number of cards in arrangement
            margin = card_width * 1.2  # Add some margin around the cards
            ax.set_xlim(-total_width / 2 - margin, total_width / 2 + margin)
            ax.set_ylim(-0.2, 1.5)
            ax.axis('off')

            # Draw cards with centered positioning
            start_x = -total_width / 2
            for i, card in enumerate(arrangement):
                create_card_patch(ax, card, start_x + i * card_spacing, 0.3,
                                  width=card_width, height=card_width * 1.4)

            # Add dotted lines between arrangements if not last in row/column
            if col < cols - 1 and arr_idx < n_arrangements - 1:
                line = plt.Line2D([1.05, 1.05], [-0.1, 1.1],
                                  transform=ax.transAxes,
                                  color='gray',
                                  linestyle=':')
                ax.add_artist(line)
            if row < actual_rows - 1 and arr_idx + cols < n_arrangements:
                line = plt.Line2D([-0.1, 1.1], [-0.15, -0.15],
                                  transform=ax.transAxes,
                                  color='gray',
                                  linestyle=':')
                ax.add_artist(line)

    # Adjust subplot spacing
    plt.subplots_adjust(wspace=0.2, hspace=0.2,
                        left=0.08, right=0.92,
                        top=0.85, bottom=0.08)

    return fig


def main():
    st.set_page_config(layout="wide", page_title="Card Arrangement Visualizer")

    st.title("Dynamic Card Arrangement Visualizer")

    # Custom CSS for card display
    st.markdown("""
        <style>
        .card-display {
            padding: 15px;
            background-color: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            text-align: center;
            font-size: 24px;
            font-family: monospace;
            letter-spacing: 5px;
        }
        .red-card {
            color: #d32f2f;
        }
        .black-card {
            color: #2f2f2f;
        }
        </style>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Individual Analysis", "Compare All Types"])

    with tab1:
        st.header("Analyze Individual Arrangement Type")

        col1, col2, col3 = st.columns(3)
        with col1:
            n = st.number_input("Number of Cards (n)",
                                min_value=2,
                                max_value=4,
                                value=3,
                                key="n1",
                                help="Select the total number of cards to use")
        with col2:
            r = st.number_input("Positions to Fill (r)",
                                min_value=1,
                                max_value=n,
                                value=2,
                                key="r1",
                                help="Select how many positions to fill")
        with col3:
            selection_type = st.selectbox(
                "Select Arrangement Type",
                ["Permutation (No Repetition)",
                 "Permutation (With Repetition)",
                 "Combination (No Repetition)",
                 "Combination (With Repetition) - Balls and Bins"],
                help="Choose the type of arrangement to analyze"
            )

        # Create deck and format cards with proper coloring
        cards = create_deck(n)

        st.write("### Available Cards")
        # Create colored card display
        card_html = ""
        for card in cards:
            color_class = "red-card" if card.suit in ['♥', '♦'] else "black-card"
            card_html += f'<span class="{color_class}">{str(card)} </span>'

        st.markdown(f"""
        <div class="card-display">
            {card_html}
        </div>
        """, unsafe_allow_html=True)

        # Calculate and display theoretical total
        total = 0
        if selection_type == "Permutation (No Repetition)":
            total = math.perm(n, r)
            formula = f"P({n},{r}) = {n}!/{(n - r)}!"
        elif selection_type == "Permutation (With Repetition)":
            total = n ** r
            formula = f"{n}^{r}"
        elif selection_type == "Combination (No Repetition)":
            total = math.comb(n, r)
            formula = f"C({n},{r}) = {n}!/({r}!*{n - r}!)"
        else:
            total = math.comb(n + r - 1, r)
            formula = f"C({n + r - 1},{r}) = ({n + r - 1})!/({r}!*{n + r - 1 - r}!)"

        col1, col2 = st.columns(2)
        with col1:
            st.write("### Formula")
            st.latex(formula)
        with col2:
            st.write("### Total Possible Arrangements")
            st.markdown(f"<h2 style='text-align: center;'>{total}</h2>", unsafe_allow_html=True)

        st.write("### Animation Controls")
        start_button = st.button("Start Animation",
                                 help="Click to start the arrangement animation", type="secondary")

        if start_button:
            with st.spinner("Generating arrangements..."):
                arrangements = animate_card_selection(cards, r, selection_type)

            st.header("All Possible Arrangements")
            with st.spinner("Creating visualization..."):
                grid_fig = create_grid_display(arrangements, selection_type)
                st.pyplot(grid_fig)
                plt.close()

    with tab2:
        st.header("Compare All Arrangement Types")

        st.markdown("""
        This view allows you to compare all four types of card arrangements side by side:
        - **Permutations vs Combinations**
        - **With vs Without Repetition**

        Adjust the parameters below to explore different scenarios.
        """)

        col1, col2 = st.columns(2)
        with col1:
            n_compare = st.number_input("Number of Cards (n)",
                                        min_value=2,
                                        max_value=4,
                                        value=3,
                                        key="n2",
                                        help="Select the total number of cards to use")
        with col2:
            r_compare = st.number_input("Positions to Fill (r)",
                                        min_value=1,
                                        max_value=n_compare,
                                        value=2,
                                        key="r2",
                                        help="Select how many positions to fill")

        cards_compare = create_deck(n_compare)

        st.write("### Available Cards for Comparison")
        # Create colored card display for comparison view
        card_html = ""
        for card in cards_compare:
            color_class = "red-card" if card.suit in ['♥', '♦'] else "black-card"
            card_html += f'<span class="{color_class}">{str(card)} </span>'

        st.markdown(f"""
        <div class="card-display">
            {card_html}
        </div>
        <br/>
        """, unsafe_allow_html=True)

        start_button = st.button("Generate Comparison",
                                 key="compare", type="secondary")

        if start_button:
            with st.spinner("Creating comparison view..."):
                arrangements_dict = create_responsive_comparison_view(cards_compare, r_compare)

        with st.expander("Need Help Understanding the Comparisons?"):
            st.markdown("""
            ### Understanding the Different Types

            **Permutations (Top Row)**
            - Order matters (ABC ≠ CBA)
            - Left: No repetition allowed
            - Right: Repetition allowed

            **Combinations (Bottom Row)**
            - Order doesn't matter (ABC = CBA)
            - Left: No repetition allowed
            - Right: Repetition allowed

            ### Tips
            - Start with small numbers (n=2, r=2) to understand the patterns
            - Compare the number of arrangements across different types
            - Notice how allowing repetition affects the total number of possibilities
            """)


if __name__ == "__main__":
    main()
