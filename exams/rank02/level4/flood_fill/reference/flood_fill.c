typedef struct s_point
{
	int	x;
	int	y;
}	t_point;

static void	fill(char **tab, t_point size, t_point p, char target)
{
	t_point	next;

	if (p.x < 0 || p.y < 0 || p.x >= size.x || p.y >= size.y
		|| tab[p.y][p.x] != target)
		return ;
	tab[p.y][p.x] = 'F';
	next = p;
	next.x = p.x + 1;
	fill(tab, size, next, target);
	next.x = p.x - 1;
	fill(tab, size, next, target);
	next.x = p.x;
	next.y = p.y + 1;
	fill(tab, size, next, target);
	next.y = p.y - 1;
	fill(tab, size, next, target);
}

void	flood_fill(char **tab, t_point size, t_point begin)
{
	if (tab[begin.y][begin.x] == 'F')
		return ;
	fill(tab, size, begin, tab[begin.y][begin.x]);
}
