#include <stdio.h>
#include <string.h>

int	ft_scanf(const char *format, ...);

typedef union u_slot
{
	int		d;
	char	c;
	char	s[512];
}	t_slot;

/* usage: ./a.out format < input */
int	main(int argc, char **argv)
{
	t_slot		slots[6];
	char		types[6];
	void		*p[6];
	const char	*f;
	int			n;
	int			ret;
	int			i;

	if (argc != 2)
		return (0);
	memset(slots, 0, sizeof(slots));
	n = 0;
	f = argv[1];
	while (*f && n < 6)
	{
		if (*f == '%' && f[1])
		{
			f++;
			types[n] = *f;
			if (*f == 'd')
				p[n] = &slots[n].d;
			else if (*f == 'c')
				p[n] = &slots[n].c;
			else
				p[n] = slots[n].s;
			n++;
		}
		f++;
	}
	i = n;
	while (i < 6)
	{
		p[i] = slots[i].s;
		i++;
	}
	ret = ft_scanf(argv[1], p[0], p[1], p[2], p[3], p[4], p[5]);
	printf("return: %d\n", ret);
	i = 0;
	while (i < ret && i < n)
	{
		if (types[i] == 'd')
			printf("%%d -> %d\n", slots[i].d);
		else if (types[i] == 'c')
			printf("%%c -> '%c' (%d)\n", slots[i].c, slots[i].c);
		else
			printf("%%s -> \"%s\"\n", slots[i].s);
		i++;
	}
	return (0);
}
