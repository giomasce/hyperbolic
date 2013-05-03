
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

inline static void swap(double *a, double *b) {

  double tmp = *b;
  *b = *a;
  *a = tmp;

}

inline static double det2(double a, double b, double c, double d) {

  return a*d - b*c;

}

inline static int solve_poly2(double a, double b, double c, double *x1, double *x2) {

  double delta = b*b - 4*a*c;
  if (delta < 0.0) {
    return 0;
  } else if (delta == 0) {
    *x1 = -b / (2*a);
    return 1;
  } else {
    double sqrtdelta = sqrt(delta);
    *x1 = (-b-sqrtdelta) / (2*a);
    *x2 = (-b+sqrtdelta) / (2*a);
    return 2;
  }

}

inline static void eupoint_line_to(double x1, double y1, double x2, double y2, double *a, double *b, double *c) {

  double deltax = x2 - x1;
  double deltay = y2 - y1;
  if (fabs(deltax) > fabs(deltay)) {
    *a = deltay / deltax;
    *b = -1.0;
    *c = y1 - *a * x1;
  } else {
    *a = -1.0;
    *b = deltax / deltay;
    *c = x1 - *b * y1;
  }

}

inline static void euline_intersection_line(double a1, double b1, double c1, double a2, double b2, double c2, double *x, double *y) {

  double denom = -det2(a1, b1, a2, b2);
  *x = det2(c1, b1, c2, b2) / denom;
  *y = det2(a1, c1, a2, c2) / denom;

}

inline static int eucircle_intersection_line(double xx, double yy, double r, double a, double b, double c, double *x1, double *y1, double *x2, double *y2) {

  int inverted = 0;
  if (fabs(a) > fabs(b)) {
    swap(&a, &b);
    swap(&xx, &yy);
    inverted = 1;
  }

  double coeff2 = 1 + a*a / b*b;
  double tmp = c / b + yy;
  double coeff1 = -2 * (xx - tmp * a / b);
  double coeff0 = xx*xx + tmp*tmp - r*r;
  int num = solve_poly2(coeff2, coeff1, coeff0, x1, x2);
  if (num >= 1) *y1 = -(c + a * *x1) / b;
  if (num == 2) *y2 = -(c + a * *x2) / b;

  if (inverted) {
    swap(x1, y1);
    swap(x2, y2);
  }

  return num;

}

static PyObject *c_eupoint_line_to(PyObject *self, PyObject *args) {

  double x1, x2, y1, y2, a, b, c;
  if (!PyArg_ParseTuple(args, "dddd", &x1, &y1, &x2, &y2)) {
    return NULL;
  }
  eupoint_line_to(x1, y1, x2, y2, &a, &b, &c);
  return Py_BuildValue("ddd", a, b, c);

}

static PyObject *c_euline_intersection_line(PyObject *self, PyObject *args) {

  double a1, b1, c1, a2, b2, c2, x, y;
  if (!PyArg_ParseTuple(args, "dddddd", &a1, &b1, &c1, &a2, &b2, &c2)) {
    return NULL;
  }
  euline_intersection_line(a1, b1, c1, a2, b2, c2, &x, &y);
  return Py_BuildValue("dd", x, y);

}

static PyObject *c_eucircle_intersection_line(PyObject *self, PyObject *args) {

  double xx, yy, r, a, b, c, x1, y1, x2, y2;
  if (!PyArg_ParseTuple(args, "dddddd", &xx, &yy, &r, &a, &b, &c)) {
    return NULL;
  }
  int num = eucircle_intersection_line(xx, yy, r, a, b, c, &x1, &y1, &x2, &y2);
  if (num == 0) {
    return Py_BuildValue("[]");
  } else if (num == 1) {
    return Py_BuildValue("[(dd)]", x1, y1);
  } else {
    return Py_BuildValue("[(dd)(dd)]", x1, y1, x2, y2);
  }

}

static PyMethodDef ChyperbolicMethods[] = {
  {"c_eupoint_line_to", c_eupoint_line_to, METH_VARARGS, ""},
  {"c_euline_intersection_line", c_euline_intersection_line, METH_VARARGS, ""},
  {"c_eucircle_intersection_line", c_eucircle_intersection_line, METH_VARARGS, ""},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initchyperbolic(void) {

  Py_InitModule3("chyperbolic", ChyperbolicMethods, "");

}
