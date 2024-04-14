import streamlit as st
import numpy as np
import pandas as pd
from itertools import combinations
from collections import Counter
import random


def is_flush(hand):
    suits = sorted([card // 13 for card in hand])
    suit_counter = Counter(suits)
    flush = False
    for count in suit_counter.values():
        if count == 5:  # If any suit appears 5 times, it's a flush
            flush = True
            break
    return flush

def is_straight(hand):
    ranks = sorted([card % 13 for card in hand])
    ranks_straigt = sorted(list(set(ranks)))
    straight = False
    leadCard=ranks_straigt
    if len(ranks_straigt) < 5:
        straight =False
        leadCard=ranks_straigt
    else:
        for i in range(len(ranks_straigt)-4):
            if (ranks_straigt[i+4] - ranks_straigt[i] == 4): 
                straight = True
                leadCard = ranks_straigt[i:i+5]
            if  (ranks_straigt[i]==0 and ranks_straigt[i+3]==3 and ranks_straigt[-1]==12):
                straight = True
                leadCard = np.concatenate([ranks_straigt[i:i+4], [ranks_straigt[-1]]])
    return straight, leadCard

def count_ranks(hand):
    ranks = [card % 13 for card in hand]
    rank_counter = Counter(ranks)
    rank_counter = dict(sorted(rank_counter.items(), key=lambda x: (x[1], x[0]), reverse=True))
    return rank_counter


def hand_value(hand):
    unsorted_suits = ([card // 13 for card in hand])
    suits = sorted(unsorted_suits)
    ranks = sorted([card % 13 for card in hand])
    suits_counter = Counter(suits)
    max_suit = max(suits_counter, key=suits_counter.get) # use for flush suite
    suit_cards = sorted([card for card, suit in zip(hand, unsorted_suits) if suit == max_suit])   # find the flush cards
    [straight, straightcard]=is_straight(hand)
    flush = is_flush(hand)
    rank_counter=count_ranks(hand)
    #first_five_elements= list(rank_counter.items())[:5]
    card_keys = [key for key, _ in list(rank_counter.items())]
    sorted_keys = sorted(card_keys,reverse=True)
    # Now first_five_keys contains the first 5 keys

    if straight and flush:
        return 8, straightcard  # Straight flush
    if rank_counter.get(card_keys[0], 0) > 3:  # Check if there are four cards of the same rank
        return 7, [int(x) for x in np.concatenate([np.ones(4) * card_keys[0], [card_keys[1]]])]  # Four of a kind
    if rank_counter.get(card_keys[0], 0) > 2:  # Check if there are three cards of the same rank
        if rank_counter.get(card_keys[1], 0)>1:  
            return 6, [int(x) for x in np.concatenate([np.ones(3) * card_keys[0], np.ones(2) * card_keys[1]])]   # Full house
        else:
            return 3, [int(x) for x in np.concatenate([np.ones(3) * card_keys[0], [card_keys[1],card_keys[2]]])]    # Three of a kind
    if flush:
        return 5, sorted(suit_cards[:5],reverse=True)  # Flush
    if straight:
        return 4, straightcard  # Straight
    if rank_counter.get(card_keys[0], 0)==2:
        if rank_counter.get(card_keys[1], 0)>1:  
            #return 3, list(np.concatenate([np.ones(2) * rank_counter.get(card_keys[0], 0), np.ones(2) * rank_counter.get(card_keys[1], 0), np.array(rank_counter.get(card_keys[2], 0))]))
            return 2, [int(x) for x in np.concatenate([np.ones(2) * card_keys[0],np.ones(2) * card_keys[1], [card_keys[2]]])]  # two pairs

        else:
            return 1, [int(x) for x in np.concatenate([np.ones(2) * card_keys[0], [card_keys[1],card_keys[2],card_keys[3]]])]   # one pairs
            
    if rank_counter.get(card_keys[0], 0)==1:
        return 0, sorted_keys[:5]  # High card

def card_to_value(card):
    suit = card.split(" ")[0]
    rank = card.split(" ")[1]
    suits = ['C', 'H', 'D', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return suits.index(suit) * 13 + ranks.index(rank) 

def calculate_probabilities(player_hands, exit_community_cards,nPlayers = 1, nScn = 10):
    num_players = len(player_hands)-1  # exclude self
    player_hands_list = []
    for i in range(len(player_hands)):
        player_hands_list = player_hands_list+ player_hands[i]
    player_probs = np.zeros(nPlayers+ num_players)  # [0] * (nPlayers+ num_players)
    player_cards_value = np.zeros(nScn)
    success=np.zeros((nScn, num_players+nPlayers))
    cards_list = np.zeros((nScn, 5))
    other_cards_list = np.zeros((nScn, 5*(num_players+nPlayers)))
    other_card_value = np.zeros((nScn, num_players+nPlayers))
    num_cards_sim = 5-len(exit_community_cards)+2*nPlayers
    rand_num = np.zeros((nScn, num_cards_sim))

    population = list(range(52))  # Numbers from 0 to 51

    # Remove numbers in player_cards from the population
    population = [num for num in population if (num not in player_hands_list and num not in exit_community_cards)]
    
    num_ccards_sim = 5-len(exit_community_cards)   #number of community cards to be generated
    # Generate 100 sets of 5 mutually exclusive random numbers
  #  sets_of_numbers = [random.sample(population, num_cards_sim) for _ in range(nScn)]
    community_cards = []
    for i in range(nScn):
        # Generate random community cards
        numbers=random.sample(population, num_cards_sim)
        community_cards = exit_community_cards + numbers[:num_ccards_sim]

        first_player_hands = player_hands[0] + community_cards   # [hand + community_cards for hand in player_hands]
        player_value, player_cards= hand_value(first_player_hands)
        player_cards_value[i]=player_value
        cards_list[i,:]=player_cards
        rand_num[i,:]=numbers
        if num_players+nPlayers>0:
            for j in range(num_players+nPlayers):
                if j<num_players:
                    Other_hands = player_hands[j+1] + community_cards
                else:
                    Other_hands = numbers[num_ccards_sim+2*(j-num_players):num_ccards_sim+2+2*(j-num_players)] +community_cards
                Other_value, other_cards = hand_value(Other_hands)
                other_cards_list[i,5*j:5*(j+1)]=other_cards
                other_card_value[i,j]=Other_value
                if player_value > Other_value:
                    success[i,j] =1
                elif player_value == Other_value:  #if same category, check card ranks
                    for k in range(5):
                        if player_cards[k]>other_cards[k]:
                            success[i,j] =1
                            break
                        elif player_cards[k]<other_cards[k]:
                            break
    
    #player_probs = [success[j]/nScn for j in range(nPlayers)]   
    player_probs = np.sum(success, axis=0)/nScn
    Winning_probs = np.sum(np.all(success == 1, axis=1))/nScn

    player_cards_value = {key: value / nScn for key, value in Counter(player_cards_value).items()}

    return player_probs, Winning_probs,player_cards_value

def main():
    st.title("Poker Probability Calculator")

    num_players = st.selectbox("Number of Players with cards known", range(1, 9))
    num_simu_players = st.selectbox("Number of Additional Players", range(0, 9-num_players))
    num_simulations = int(st.slider("Number of Games to simulate", 100, 100000, step=100,value = 10000))
    

    # Generate options for card selection
    card_options = [f"{suit} {rank}" for suit in ['C', 'H', 'D', 'S'] for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']]

    player_hands = []
    for i in range(num_players):
        player_hand1 = st.selectbox(f"Player {i+1} Hand - Card 1", card_options,index=False)   # Two cards per player
        card_options = [card for card in card_options if card != player_hand1]
        player_hand2 = st.selectbox(f"Player {i+1} Hand - Card 2", card_options,index=False)   # Two cards per player
        card_options = [card for card in card_options if card != player_hand2]
        player_hands.append([card_to_value(player_hand1),card_to_value(player_hand2) ])

       # player_hand = [st.selectbox(f"Player {i+1} Hand - Card {j+1}", card_options,index=False) for j in range(2)]  # Two cards per player
        #st.write(f'player hand{player_hand}')
        #player_hands.append([card_to_value(card) for card in player_hand])
    community_cards = []
    statusOptions = ["Pre-flop", "Flop", "Turn", "River"]
    status = st.selectbox("Status", statusOptions)
    status_index = statusOptions.index(status)

    if status_index>0:  #post flop
        flop_card1=st.selectbox(f"Flop Card 1", card_options)
        card_options = [card for card in card_options if card != flop_card1]
        flop_card2=st.selectbox(f"Flop Card 2", card_options)
        card_options = [card for card in card_options if card != flop_card2]
        flop_card3=st.selectbox(f"Flop Card 3", card_options)
        card_options = [card for card in card_options if card != flop_card3]
        community_cards.extend([card_to_value(flop_card1),card_to_value(flop_card2),card_to_value(flop_card3)])

    if status_index>1:  #turn
        turn_card=st.selectbox(f"Turn Card", card_options)
        card_options = [card for card in card_options if card != turn_card]
        community_cards.append(card_to_value(turn_card))

    if status_index>2:  # river
        community_cards.append(card_to_value(st.selectbox("River card", card_options)))

    if st.button("Calculate"):
        player_probs, Winning_probs, Card_Cat_probs = calculate_probabilities(player_hands, community_cards,num_simu_players, num_simulations)
        
        for i, prob in enumerate(player_probs):
            st.write(f"**Winning Probability against Player {i+2}:** <span style='color:darkviolet'>{prob:.2%}</span>", unsafe_allow_html=True)
            #st.write(f"Winning Probability against Player {i+1}: {prob:.2%}")
        st.write(f"**Winning Probability against all other players:** <span style='color:red'>{Winning_probs:.2%}</span>", unsafe_allow_html=True)

        st.write(f"**Royal Flush Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(8, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Four of a kind Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(7, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Full House Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(6, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Flush Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(5, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Straight Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(4, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Three of a kind Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(3, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**Two Pairs Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(2, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**One Pair Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(1, 0):.2%}</span>", unsafe_allow_html=True)
        st.write(f"**High cards Probabilities:** <span style='color:blue'>{Card_Cat_probs.get(0, 0):.2%}</span>", unsafe_allow_html=True)
        

def main_test():
    hand = [17,0, 1, 2,3,14,28]
    hand1 = [18,0, 1, 2,3,14,25]
    hand2= [17,14, 1, 2, 3,14,27]
    hand3 = [17,14, 1, 2, 3,14,28]
    hand4 = [41,13,27,10,3,12,51]

if __name__ == "__main__":
    main()
