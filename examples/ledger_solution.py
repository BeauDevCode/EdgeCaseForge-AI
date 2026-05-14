def solve(input_data: str) -> str:
    lines = [line.strip() for line in input_data.strip().splitlines() if line.strip()]
    n = int(lines[0])
    seen = set()
    balances = {}
    touched = set()

    for i in range(1, n + 1):
        tx_id, account_id, amount, status = lines[i].split()

        if tx_id in seen:
            continue
        seen.add(tx_id)

        if status != "POSTED":
            continue

        amount = int(amount)
        balances[account_id] = balances.get(account_id, 0) + amount
        touched.add(account_id)

    return "\n".join(f"{acct} {balances.get(acct, 0)}" for acct in sorted(touched))
