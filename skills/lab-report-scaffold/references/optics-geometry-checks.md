# Optics geometry checks

Relations for inclined-reflector and thin-lens labs, written out so a script can be
checked against a known value instead of against memory. Verified on ECE 5331 Lab 3
(Pepper's ghost pyramid): the Fresnel branch reproduces the 4.9 percent and 6.2
percent figures quoted for a 45 degree face, which is the check that the incidence
convention is right.

## Inclined plane reflector

A source at perpendicular offset `p` from a plane through the hinge, inclined at
`alpha` to the base plane, with unit normal `n = (sin alpha, cos alpha)`, mirrors to
`S' = S + 2 p n`. Two scalars fall out and they are the whole answer:

- height above the base plane: `h = p sin(2 alpha)`, maximum at `alpha = 45` degrees
- lateral position from the hinge: `hinge - p cos(2 alpha)`, so past 45 degrees the
  image walks outward beyond the base edge and inside 45 it moves over the base

Rotating the mirror by `theta` rotates the image by `2 theta` about the hinge line.

Numbers for a 45 to 60 degree angle test on the same base: the image turns 30
degrees, sits at 86.7 percent of the 45 degree height, and lands `0.50 p` outside
the hinge. At exactly 45 degrees it sits directly above the hinge, which is why the
four faces of a frustum land four views on the axis instead of four offset copies.

## Frustum face geometry

- face angle: `alpha = atan2(rise, (b - a) / 2)`, `b` the base edge, `a` the top edge
- slant: `s = hypot(rise, (b - a) / 2)`
- 45 degree condition: `rise = (b - a) / 2`, equivalently `tan alpha = 1`
- print check: `cos(alpha) = ((b - a) / 2) / s` gives 0.707 at 45 degrees. Divide by
  the slant, never by the rise: the rise ratio reads 1.000 at 45 and 0.707 at 60 and
  inverts the answer

Base 50 mm, top 10 mm: 45 degrees gives rise 20.0 mm and slant 28.3 mm; 60 degrees
gives rise 34.6 mm and slant 40.0 mm. Base 90 mm, top 30 mm: rise 30.0 mm and slant
42.4 mm at 45 degrees.

## Single-surface Fresnel, unpolarized

For a face inclined `alpha` where the exit ray is horizontal, the incidence angle is
`i = 90 - alpha` (45 degrees of incidence on a 45 degree face, 30 on a 60 degree
face). Then `sin t = sin i / n`,

- `Rs = ((cos i - n cos t) / (cos i + n cos t))^2`
- `Rp = ((n cos i - cos t) / (n cos i + cos t))^2`
- `R = (Rs + Rp) / 2`

Values to verify against, at 550 nm:

| material | n | incidence 45 | incidence 30 |
|---|---|---|---|
| acrylic | 1.49 | 4.88% | 4.02% |
| polycarbonate | 1.58 | 6.16% | 5.20% |

A ghost reaching the eye at about 5 percent of screen brightness per face is why the
room must be dark and the display at maximum, and why steepening the face dims the
image on top of compressing it.

## Thin lens, when the lab is a focal length measurement

`1/u + 1/v = 1/f` with `M = v/u` gives `1/M = u/f - 1`: slope `1/f`, crossing at
`u = f`. Quote the slope, treat the crossing as a sanity check. The estimator
conditioning and same-axis enlargement traps are in the parent skill.
