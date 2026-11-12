#include <stdlib.h>
#include <unistd.h>

static void	put_nbr(int n)
{
	char	c;

	if (n >= 10)
		put_nbr(n / 10);
	c = '0' + n % 10;
	write(1, &c, 1);
}

static void	print_solution(int *rows, int n)
{
	int	i;

	i = 0;
	while (i < n)
	{
		if (i)
			write(1, " ", 1);
		put_nbr(rows[i]);
		i++;
	}
	write(1, "\n", 1);
}

static int	is_safe(int *rows, int col, int row)
{
	int	c;

	c = 0;
	while (c < col)
	{
		if (rows[c] == row || rows[c] - row == col - c || row - rows[c] == col - c)
			return (0);
		c++;
	}
	return (1);
}

static void	solve(int *rows, int col, int n)
{
	int	row;

	if (col == n)
	{
		print_solution(rows, n);
		return ;
	}
	row = 0;
	while (row < n)
	{
		if (is_safe(rows, col, row))
		{
			rows[col] = row;
			solve(rows, col + 1, n);
		}
		row++;
	}
}

int	main(int argc, char **argv)
{
	int	n;
	int	*rows;

	if (argc != 2)
		return (1);
	n = atoi(argv[1]);
	if (n <= 0)
		return (0);
	rows = malloc(sizeof(int) * n);
	if (!rows)
		return (1);
	solve(rows, 0, n);
	free(rows);
	return (0);
}
