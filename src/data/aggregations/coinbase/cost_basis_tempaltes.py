# How to implement a fifo

AMOUNT = 'amount_changed_coin'
RATE = 'rate'
#Eth cost basis
bought = [{'amount_changed_coin': 123.4095, 'rate': 354.73492659640436}, {'amount_changed_coin': 10.8, 'rate': 483.07931955910755}, {'amount_changed_coin': 0.06850164, 'rate': 1401.426301618472}, {'amount_changed_coin': 1.01379042, 'rate': 1282.3163193828561}, {'amount_changed_coin': 1.0, 'rate': 864.63}, {'amount_changed_coin': 0.18831272, 'rate': 1115.1663042199168}, {'amount_changed_coin': 0.7209, 'rate': 868.6919128866695}, {'amount_changed_coin': 2.99010994, 'rate': 838.7785233074072}, {'amount_changed_coin': 2.58794718, 'rate': 386.40664992243}, {'amount_changed_coin': 0.38626513, 'rate': 388.3343029177912}, {'amount_changed_coin': 0.59265536, 'rate': 421.83031973253395}, {'amount_changed_coin': 0.63025534, 'rate': 396.66462802203307}, {'amount_changed_coin': 0.53108095, 'rate': 470.7380296732542}, {'amount_changed_coin': 0.53055393, 'rate': 471.2056321965234}, {'amount_changed_coin': 0.2718428, 'rate': 551.789490102368}, {'amount_changed_coin': 0.40184161, 'rate': 622.1356718135785}, {'amount_changed_coin': 0.0, 'rate': 600.21}]

sold = [{'amount_changed_coin': -123.4095, 'rate': 339.00673997871587}, {'amount_changed_coin': -10.8, 'rate': 474.49077384217105}, {'amount_changed_coin': -0.25681436, 'rate': 1065.4778027210004}, {'amount_changed_coin': -1.0, 'rate': 1028.38}, {'amount_changed_coin': -1.73469042, 'rate': 822.3830509192528}, {'amount_changed_coin': -2.7, 'rate': 859.2888888888888}, {'amount_changed_coin': -2.10470929, 'rate': 445.05433812191706}]

total = 0
for x in sold:
    total += x['amount_changed_coin'] 

total_bought = 0
for x in bought:
    total_bought += x['amount_changed_coin'] 

def fifo(bought, sold):
    #Run fifo method
    bought_iter = 0
    curr_bought = bought[bought_iter][AMOUNT]
    fifo_list = []
    

    for trans in sold:
        curr_sold = abs(trans[AMOUNT])

        while(curr_sold != 0):
            # if what we sold is greater than purchase
            # reduce from amount we sold then go to the next transaction where we purchased.
            if curr_sold >= curr_bought:
                curr_sold -= curr_bought
                add_trans = ({'amount' : curr_bought , 'sold_rate' : trans['rate'], 'bought_rate' : bought[bought_iter]['rate']})
                try:
                    bought_iter += 1
                    curr_bought = bought[bought_iter][AMOUNT]
                    fifo_list.append(add_trans)
                except Exception as error:
                    print('There are more sold than there were purchased !')
            else:
                curr_bought -= curr_sold
                add_trans = ({'amount' : curr_sold , 'sold_rate' : trans['rate'], 'bought_rate' : bought[bought_iter]['rate']})
                fifo_list.append(add_trans)
                curr_sold = 0
            # print(add_trans)
    amount = 0
    for x in fifo_list:
        amount += x['amount']
    print(amount)

fifo(bought,sold)

print('total sold ' , total)

total = 0
for x in sold:
    total += x['amount_changed_coin'] 
    # print(total)
