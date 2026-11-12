#include <stdlib.h>

int	*ft_range(int start, int end)
{
	int	*tab;
	int	len;
	int	step;
	int	i;

	len = (end >= start ? end - start : start - end) + 1;
	step = (end >= start ? 1 : -1);
	tab = malloc(sizeof(int) * len);
	if (!tab)
		return (NULL);
	i = 0;
	while (i < len)
	{
		tab[i] = start + i * step;
		i++;
	}
	return (tab);
}
